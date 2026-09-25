"""Build a complete, source-verified directory/inheritance browser for game headers."""
import argparse
import collections
import html
import json
import re
import runpy
import subprocess
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'cpp-schema.py'))
U = runpy.run_path(str(HERE / 'build-field-usage.py'))
VERSION = 'tree-1'


def comment_before(raw, row):
    lines = raw.decode('utf-8-sig').splitlines()
    i = row - 1
    # Reflection annotations can separate a declaration from its documentation.
    if i >= 0 and re.match(r'\s*U(?:CLASS|STRUCT|ENUM|INTERFACE|FUNCTION|PROPERTY)\b', lines[i]):
        i -= 1
    out = []
    while i >= 0 and lines[i].strip().startswith(('//', '/*', '*')):
        s = re.sub(r'^[/\s*]+|[\s*/]+$', '', lines[i].strip())
        if s and not re.fullmatch(r'[-=]+', s) and not re.search(r'---|Copyright', s):
            out.insert(0, s)
        i -= 1
    return ' '.join(out)


def inventory(repo, sha):
    base = f'https://github.com/wighs33/Pandora-Battle/blob/{sha}/'
    link = lambda path, line: base + quote(path, safe='/') + '#L' + str(line)
    nodes = {}
    paths = subprocess.check_output(['git', '-C', str(repo), 'ls-files', 'Source/LabProject'], encoding='utf8').splitlines()
    for path in paths:
        if not path.endswith('.h'):
            continue
        raw = (repo / path).read_bytes()
        root = P['PARSER'].parse(P['sanitize'](raw)).root_node
        for n in P['walk'](root):
            if n.type not in P['DEFINITION_TYPES'] | {'namespace_definition', 'enum_specifier'}:
                continue
            body, name_node = n.child_by_field_name('body'), n.child_by_field_name('name')
            if body is None or name_node is None:
                continue
            name = P['text'](name_node)
            kind = {'namespace_definition':'namespace', 'enum_specifier':'enum'}.get(n.type, n.type.split('_')[0])
            if kind == 'namespace' and not any(c.type in ('declaration','function_definition') for c in body.named_children):
                continue
            if n.has_error:
                raise ValueError(f'Parse error: {path}:{n.start_point.row+1} {name}')
            fields, methods, values = [], [], []
            access = 'private' if kind == 'class' else 'public'
            for m in body.named_children:
                if m.type == 'access_specifier':
                    access = P['text'](m)
                    continue
                if m.type == 'enumerator':
                    values.append(dict(name=P['text'](m.child_by_field_name('name')), declaration=raw[m.start_byte:m.end_byte].decode('utf8'), url=link(path,m.start_point.row+1)))
                    continue
                if m.type not in ('field_declaration','declaration','function_definition'):
                    continue
                declarator = m.child_by_field_name('declarator')
                if declarator is None:
                    continue
                fn = next((c for c in P['walk'](declarator) if c.type == 'function_declarator'), None)
                line = m.start_point.row + 1
                if fn is not None:
                    fn_body = m.child_by_field_name('body')
                    end = fn_body.start_byte if fn_body is not None else m.end_byte
                    declaration = re.sub(r'\s+', ' ', raw[m.start_byte:end].decode('utf8')).strip()
                    methods.append(dict(name=P['text'](U['named_declarator'](fn)), declaration=declaration, access=access,
                        comment=comment_before(raw,m.start_point.row), path=path,line=line,url=link(path,line)))
                elif kind in ('class','struct','union'):
                    for d in m.children_by_field_name('declarator'):
                        key = P['text'](U['named_declarator'](d))
                        if not re.fullmatch(r'\w+',key):
                            raise ValueError(f'Unhandled member: {name}.{key}')
                        fields.append(dict(key=key,declaration=re.sub(r'\s+',' ',raw[m.start_byte:m.end_byte].decode('utf8')).strip(),
                            access=access,line=line,path=path,url=link(path,line),types=[x[0] for x in P['declared_types'](m.child_by_field_name('type'))]))
            bases = next((c for c in n.named_children if c.type == 'base_class_clause'),None)
            entry = dict(name=name,qualified=P['qualified_name'](n),kind=kind,path=path,line=n.start_point.row+1,
                url=link(path,n.start_point.row+1),fields=fields,methods=methods,values=values,
                bases=P['base_types'](bases),comment=comment_before(raw,n.start_point.row),
                folder=str(Path(path).parent).replace('\\','/').removeprefix('Source/LabProject').strip('/'),
                highlights=[],role=name,purpose='',storage={'class':'C++ 클래스','struct':'데이터 구조체','namespace':'함수 네임스페이스','enum':'열거형'}.get(kind,kind))
            if name in nodes:
                if kind != 'namespace' or nodes[name]['kind'] != 'namespace':
                    raise ValueError('Ambiguous symbol: '+name)
                nodes[name]['methods'].extend(methods)
                continue
            nodes[name] = entry
    return nodes


def build(repo):
    git = lambda *args: subprocess.check_output(['git','-C',str(repo),*args],encoding='utf8').strip()
    if git('status','--porcelain'):
        raise ValueError('Source checkout must be clean')
    sha = git('rev-parse','HEAD')
    types = inventory(repo,sha)
    notes = runpy.run_path(str(HERE/'core-class-content.py'))['notes']()
    overrides = runpy.run_path(str(HERE/'class-tree-content.py'))['NOTES']
    def expand(field, depth=0, seen=()):
        result = {**field,'references':[t for t in field['types'] if t in types],'schemas':[]}
        for name in dict.fromkeys(field['types']):
            child = types.get(name)
            if child and child['kind']=='struct' and name not in seen and depth<2:
                result['schemas'].append({k:child[k] for k in ('name','url','path','line')} | {
                    'fields':[expand(f,depth+1,seen+(name,)) for f in child['fields']]})
        return result
    for name,n in types.items():
        old = notes.get(name,{})
        n['role'] = overrides.get(name,{}).get('role',old.get('role',name))
        n['purpose'] = overrides.get(name,{}).get('purpose') or n['comment'] or old.get('purpose') or (
            f'{n["folder"] or "LabProject"}의 {n["storage"]}입니다. '+
            (f'{", ".join(n["bases"])}를 상속합니다. ' if n['bases'] else '')+
            (f'선언된 주요 함수는 {", ".join(m["name"] for m in n["methods"][:4])}입니다.' if n['methods'] else '선언된 데이터와 해당 데이터를 읽고 변경하는 함수를 아래에 표시합니다.'))
        fields = {f['key'] for f in n['fields']}
        n['highlights'] = [{**h,'keys':[k for k in h['keys'] if k in fields]} for h in old.get('highlights',[]) if fields & set(h['keys'])]
    # Expand against raw schemas, before replacing the inventory's own field lists.
    expanded = {name:[expand(f) for f in n['fields']] for name,n in types.items()}
    for name,n in types.items():
        n['fields'] = expanded[name]
    nodes = sorted(types.values(),key=lambda n:(n['folder'].lower(),n['name'].lower()))
    counts = dict(collections.Counter(n['kind'] for n in nodes))
    inheritance = [dict(source=n['name'],target=b,url=n['url'],external=b not in types) for n in nodes for b in n['bases']]
    data = dict(meta=dict(commit=sha,sourceDate=git('show','-s','--format=%cI','HEAD'),
        engine=json.loads((repo/'LabProject.uproject').read_text(encoding='utf-8-sig'))['EngineAssociation'],
        counts=counts,typeCount=len(nodes),classCount=counts.get('class',0),headerCount=len({n['path'] for n in nodes}),
        version=VERSION,scope='Source/LabProject/**/*.h'),nodes=nodes,inheritance=inheritance)
    site = HERE.parent/'pandora-battle-portfolio'
    (site/'assets/class-map-data.js').write_text('window.PANDORA_CLASS_MAP = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8',newline='\n')
    rows = ''.join(f'<li><a href="class-map.html?v={VERSION}&amp;class={quote(n["name"])}">{html.escape(n["qualified"])} — {n["storage"]}</a> <a href="{n["url"]}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></li>' for n in nodes)
    (site/'class-index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pandora Battle · 전체 클래스 목록</title><link rel="stylesheet" href="assets/class-map.css?v={VERSION}"><main class="atlas"><a href="class-map.html?v={VERSION}">← 전체 클래스 트리</a><h1>전체 클래스와 데이터 선언</h1><p>Source/LabProject · {sha[:12]}</p><ul class="source-index">{rows}</ul></main></html>\n',encoding='utf8',newline='\n')
    print(json.dumps(data['meta'],ensure_ascii=False))
    U['build'](repo)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('repo',type=Path)
    build(parser.parse_args().repo.resolve())
