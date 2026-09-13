"""Build the portfolio's C++ header graph from a clean Pandora-Battle checkout.

Requires: tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
Usage: python tools/build-class-map.py PATH_TO_GAME_REPO
Named definitions in tracked headers and implementation files are nodes. Preprocessor branches are
read together; Unreal annotations are masked, preserving byte offsets and lines.
Relations describe declarations, not runtime calls or ownership.
"""
import argparse
import collections
import html
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

from tree_sitter import Language, Parser
import tree_sitter_cpp

PARSER = Parser(Language(tree_sitter_cpp.language()))
DEFINITION_TYPES = {"class_specifier", "struct_specifier", "union_specifier"}


def walk(node):
    yield node
    for child in node.named_children:
        yield from walk(child)


def blank(value):
    return re.sub(rb"[^\r\n]", b" ", value)


def sanitize(source):
    # Mask comments and quoted literals before balanced annotation scanning.
    source = re.sub(rb'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                    lambda m: m[0][:1] + blank(m[0][1:-1]) + m[0][-1:] if m[0][:1] in (b'"', b"'") else blank(m[0]), source)
    source = re.sub(rb"^[ \t]*#(?:\\\r?\n|[^\n])*", lambda m: blank(m[0]), source, flags=re.M)
    annotation = rb"\b(?:UCLASS|USTRUCT|UINTERFACE|UENUM|UPROPERTY|UFUNCTION|UPARAM|UMETA|GENERATED_[A-Z_]+|DECLARE_[A-Za-z_]+|UE_DEPRECATED|UE_NONCOPYABLE|ATTRIBUTE_ACCESSORS|__pragma|MSVC_PRAGMA|PURE_VIRTUAL)\s*\("
    edits = []
    for match in re.finditer(annotation, source):
        depth, end = 1, match.end()
        while end < len(source) and depth:
            if source[end] == 40:
                depth += 1
            elif source[end] == 41:
                depth -= 1
            end += 1
        edits.append((match.start(), end))
    data = bytearray(source)
    for start, end in edits:
        data[start:end] = blank(source[start:end])
    clean = re.sub(rb"\b(?:[A-Z][A-Z0-9_]*_API|FORCEINLINE_DEBUGGABLE|FORCEINLINE|UE_NODISCARD)\b", lambda m: blank(m[0]), bytes(data))
    clean = re.sub(rb"\bPACKAGE_SCOPE\b", b"public       ", clean)
    # Normalize grammar gaps that cannot change the declared type relationships.
    clean = re.sub(rb"=\s*\{\s*\}", lambda m: blank(m[0]), clean)
    return re.sub(rb":\s*\d+(?=\s*=)", lambda m: blank(m[0]), clean)


def text(node):
    return node.text.decode("utf-8") if node else ""


def qualified_name(node):
    name = text(node.child_by_field_name("name"))
    parent = node.parent
    while parent:
        if parent.type in DEFINITION_TYPES | {"namespace_definition"}:
            prefix = text(parent.child_by_field_name("name"))
            if prefix:
                name = prefix + "::" + name
        parent = parent.parent
    return name


def definitions(clean):
    return [m for m in re.finditer(rb"\b(?:class|struct|union)\s+(?:[A-Za-z_]\w*\s+)?([A-Za-z_]\w*)\s*(?:final\s*)?(?:\:[^;{}]*)?\{", clean)
            if not re.search(rb"\benum\s+$", clean[:m.start()])]


def implementation_definitions(clean):
    # Parse only explicit type definitions in .cpp files. Leave function bodies
    # outside definitions blank, preserving source line positions.
    data = bytearray(blank(clean))
    for match in definitions(clean):
        depth, end = 1, match.end()
        while end < len(clean) and depth:
            if clean[end] == 123:
                depth += 1
            elif clean[end] == 125:
                depth -= 1
            end += 1
        if depth:
            raise ValueError("Unbalanced implementation definition")
        while end < len(clean) and clean[end] in b" \r\n\t":
            end += 1
        if end < len(clean) and clean[end] == 59:
            end += 1
        data[match.start():end] = clean[match.start():end]
    return bytes(data)


def group_for(path):
    parts = path.split("/")
    if parts[0] == "Plugins":
        return parts[1], "plugin", parts[1]
    module = parts[1]
    if module == "LabProjectEditor":
        return "Editor", "editor", module
    group = parts[2] if len(parts) > 3 else "Core"
    return group, "game", module


def declared_types(root):
    """Type tokens only; ignore bodies/default values and nested definitions."""
    if root is None:
        return []
    skip = {"compound_statement", "initializer_list", "argument_list", "default_value", "comment"}
    found = []

    def visit(node):
        if node is not root and (node.type in skip or node.type in DEFINITION_TYPES):
            # 'class UFoo*' is an elaborated type, not a nested definition.
            if node.type in DEFINITION_TYPES and not node.child_by_field_name("body"):
                name = node.child_by_field_name("name")
                if name:
                    found.append((text(name), name.start_point.row + 1))
            return
        if node.type == "type_identifier":
            found.append((text(node), node.start_point.row + 1))
        for child in node.named_children:
            visit(child)

    visit(root)
    return found


def build(repo, output):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args]).decode("utf-8").strip()
    commit = git("rev-parse", "HEAD")
    tracked = git("ls-tree", "-r", "--name-only", "HEAD", "Source", "Plugins").splitlines()
    headers = [p for p in tracked if p.endswith((".h", ".hpp", ".hh")) and "/ThirdParty/" not in p]
    implementations = [p for p in tracked if p.endswith((".cpp", ".cc", ".cxx")) and "/ThirdParty/" not in p]
    files = headers + implementations
    dirty = git("diff", "HEAD", "--name-only", "--", "*.h", "*.hpp", "*.hh", "*.cpp", "*.cc", "*.cxx")
    if dirty:
        raise ValueError("Use a clean checkout: header URLs are pinned to HEAD")
    nodes, ast, errors, coverage = [], {}, [], []
    for path in files:
        original = (repo / path).read_bytes()
        clean = sanitize(original)
        implementation = path in implementations
        if implementation:
            clean = implementation_definitions(clean)
        root = PARSER.parse(clean).root_node
        parsed_lines = set()
        for node in walk(root):
            if node.type == "ERROR" or node.is_missing:
                errors.append({"path": path, "line": node.start_point.row + 1, "text": text(node)[:180]})
            if node.type not in DEFINITION_TYPES or not node.child_by_field_name("body"):
                continue
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name, line = text(name_node), name_node.start_point.row + 1
            qualified = qualified_name(node)
            group, origin, module = group_for(path)
            key = path + ":" + qualified
            if key in ast:
                # Multiple preprocessor definitions would need disambiguation.
                raise ValueError("Duplicate definition: " + key)
            bases = next((n for n in node.named_children if n.type == "base_class_clause"), None)
            base_names = [text(n) for n in bases.named_children if n.type != "access_specifier"] if bases else []
            nodes.append({"id": key, "name": name, "qualified": qualified, "kind": node.type.split("_")[0],
                          "path": path, "line": line, "group": group, "origin": origin, "module": module,
                          "bases": base_names, "implementation": implementation,
                          "url": f"https://github.com/wighs33/Pandora-Battle/blob/{commit}/{quote(path)}#L{line}"})
            ast[key] = node
            parsed_lines.add(node.start_point.row + 1)
        # Independent lexical inventory catches definitions swallowed by a parse error.
        expected = definitions(clean)
        missed = [clean[:m.start()].count(b"\n") + 1 for m in expected if clean[:m.start()].count(b"\n") + 1 not in parsed_lines]
        if missed:
            coverage.append({"path": path, "lines": missed})
    lookup = collections.defaultdict(list)
    for node in nodes:
        lookup[node["name"]].append(node)
    relations = {}
    unresolved = []
    for owner in nodes:
        node = ast[owner["id"]]
        body = node.child_by_field_name("body")
        refs = []
        bases = next((n for n in node.named_children if n.type == "base_class_clause"), None)
        refs.extend((name, "inheritance", line) for name, line in declared_types(bases))
        # Flatten conditional branches without descending into nested classes.
        def members(parent):
            for member in parent.named_children:
                if member.type.startswith("preproc_"):
                    yield from members(member)
                else:
                    yield member
        for member in members(body):
            if member.type not in {"field_declaration", "function_definition", "declaration", "alias_declaration", "type_definition"}:
                continue
            is_function = member.type == "function_definition" or any(n.type == "function_declarator" for n in walk(member) if n.type != "compound_statement")
            relation = "signature" if is_function or member.type in {"alias_declaration", "type_definition"} else "member"
            refs.extend((name, relation, line) for name, line in declared_types(member))
        for name, kind, line in refs:
            candidates = lookup.get(name, [])
            if len(candidates) > 1:
                local = [n for n in candidates if n["path"] == owner["path"]]
                candidates = local if len(local) == 1 else candidates
            if len(candidates) != 1:
                if len(candidates) > 1:
                    unresolved.append({"owner": owner["id"], "name": name, "line": line})
                continue
            target = candidates[0]
            if target["id"] == owner["id"]:
                continue
            key = (owner["id"], target["id"], kind)
            if key not in relations:
                relations[key] = {"source": owner["id"], "target": target["id"], "kind": kind, "line": line}
    nodes.sort(key=lambda n: (n["group"].lower(), n["qualified"].lower()))
    edges = sorted(relations.values(), key=lambda e: (e["source"], e["target"], e["kind"]))
    data = {"meta": {"repository": "wighs33/Pandora-Battle", "commit": commit, "sourceDate": git("show", "-s", "--format=%cI", "HEAD"),
                     "headers": len(headers), "implementations": len(implementations), "implementationTypes": sum(n["implementation"] for n in nodes),
                     "classes": sum(n["kind"] == "class" for n in nodes), "structs": sum(n["kind"] == "struct" for n in nodes),
                     "relations": dict(collections.Counter(e["kind"] for e in edges))}, "nodes": nodes, "edges": edges}
    report = {"meta": data["meta"], "nodes": len(nodes), "edges": len(edges), "origins": dict(collections.Counter(n["origin"] for n in nodes)),
              "groups": dict(collections.Counter(n["group"] for n in nodes)), "parseErrors": errors, "missedDefinitions": coverage, "ambiguousReferences": unresolved}
    if coverage or unresolved or errors:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise ValueError("Resolve parser errors or uncovered/ambiguous declarations before publishing")
    output.mkdir(parents=True, exist_ok=True)
    (output / "class-map-data.js").write_text("// Generated by tools/build-class-map.py; source revision is pinned.\nwindow.PANDORA_CLASS_MAP = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    rows = []
    for group in sorted({n["group"] for n in nodes}):
        rows.append(f'<section><h2>{html.escape(group)}</h2><ul>')
        for node in (n for n in nodes if n["group"] == group):
            rows.append(f'<li><a href="{html.escape(node["url"])}" target="_blank" rel="noopener noreferrer">'
                        f'{html.escape(node["qualified"])} ↗</a><small>{node["kind"]} · '
                        f'{html.escape(node["path"])}:{node["line"]}</small></li>')
        rows.append('</ul></section>')
    (output.parent / "class-index.html").write_text(
        '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Pandora Battle · 전체 클래스 링크 목록</title><link rel="stylesheet" href="assets/class-map.css"></head>'
        '<body><main class="source-index"><a href="class-map.html">← 인터랙티브 관계도</a><h1>전체 클래스 링크 목록</h1>'
        f'<p>{len(nodes)}개 타입 · {data["meta"]["classes"]}개 클래스 · {data["meta"]["structs"]}개 구조체. '
        '브라우저의 페이지 찾기(Ctrl + F)로 검색할 수 있습니다. 각 링크는 GitHub의 선언 줄로 연결됩니다.</p>'
        + '\n'.join(rows) + '</main></body></html>', encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("repository", type=Path)
    cli.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "pandora-battle-portfolio/assets")
    args = cli.parse_args()
    build(args.repository.resolve(), args.output.resolve())
