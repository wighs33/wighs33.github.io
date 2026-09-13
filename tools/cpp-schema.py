"""Unreal-aware C++ parsing helpers. Mask annotations while preserving source offsets."""
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

