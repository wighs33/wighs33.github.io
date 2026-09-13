"""Build the curated atlas from verified header fields and reviewed semantic flows."""
import argparse
import html
import json
import re
import runpy
import subprocess
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'cpp-schema.py'))

def build(repo):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True, encoding='utf8').strip()
    if git('status', '--porcelain'):
        raise ValueError('Source checkout must be clean')
    sha = git('rev-parse', 'HEAD')
    base = f'https://github.com/wighs33/Pandora-Battle/blob/{sha}/'
    def url(path, line):
        return base + quote(path, safe='/') + '#L' + str(line)
    types, texts = {}, {}
    for path in git('ls-files', 'Source').splitlines():
        if not path.endswith('.h'):
            continue
        raw = (repo / path).read_bytes()
        texts[path] = raw.decode('utf-8-sig')
        tree = P['PARSER'].parse(P['sanitize'](raw))
        for n in P['walk'](tree.root_node):
            if n.type not in ('class_specifier', 'struct_specifier') or not n.child_by_field_name('body'):
                continue
            name = P['text'](n.child_by_field_name('name'))
            if not name:
                continue
            fields = []
            for m in n.child_by_field_name('body').named_children:
                if m.type not in ('field_declaration', 'declaration'):
                    continue
                d = m.child_by_field_name('declarator')
                if d is None or any(x.type == 'function_declarator' for x in P['walk'](m)):
                    continue
                while d.child_by_field_name('declarator'):
                    d = d.child_by_field_name('declarator')
                key = P['text'](d)
                if not re.fullmatch(r'\w+', key):
                    raise ValueError(f'Unhandled field declarator: {name}.{key}')
                declaration = re.sub(r'\s+', ' ', raw[m.start_byte:m.end_byte].decode('utf8')).strip()
                line = m.start_point.row + 1
                fields.append(dict(key=key, declaration=declaration, line=line, path=path,
                    url=url(path, line), types=[x[0] for x in P['declared_types'](m.child_by_field_name('type'))]))
            bases = next((c for c in n.named_children if c.type == 'base_class_clause'), None)
            entry = dict(name=name, path=path, line=n.start_point.row + 1,
                url=url(path, n.start_point.row + 1), fields=fields,
                bases=[x[0] for x in P['declared_types'](bases)], kind=n.type.split('_')[0], parseError=n.has_error)
            types[name] = None if name in types else entry
    groups = json.loads((HERE / 'core-class-selection.json').read_text(encoding='utf8'))
    notes = runpy.run_path(str(HERE / 'core-class-content.py'))['notes']()
    selected = [n for g in groups for n in g['names']]
    assert len(selected) == len(set(selected)) == 100 and set(selected) == set(notes)
    essentials = '''APdPlayerState UPandoraComponent UPandoraDefinition USkillDefinition UPandoraTreeComponent UPandoraSkillSource FPandoraSkillBinder UPdAbilitySystemComponent UBasicAttributeSet UPdGameplayAbility APdPlayer ACharacterBase APdPlayerController UInventoryComponent UItemInstance UItemDefinition UEquipmentComponent UCombatComponent UExperienceManagerComponent UExperienceDefinition AExperienceGameMode AExperienceGameState UOnlineSessionsSubsystem ALobbyGameMode ALobbyGameState UPlayerProfileSubsystem UPdSaveGame USelectingPandoraAndWeaponComponent UContentDataSubsystem UPlayerMatchComponent'''.split()
    order = essentials + [n for n in selected if n not in essentials]
    nodes, errors = [], []
    def expand(field, depth=0, seen=()):
        result = {**field, 'references': [t for t in field['types'] if t in selected]}
        nested = []
        for name in dict.fromkeys(field['types']):
            child = types.get(name)
            if child and child['kind'] == 'struct' and name not in seen and depth < 2:
                nested.append({k: child[k] for k in ('name','url','path','line')} | {
                    'fields': [expand(f, depth + 1, seen + (name,)) for f in child['fields']]})
        result['schemas'] = nested
        return result
    for group in groups:
        for name in group['names']:
            meta = types.get(name)
            if not meta or meta['kind'] != 'class':
                raise ValueError(f'Missing/ambiguous class: {name}')
            if meta['parseError']:
                raise ValueError(f'Parser error in selected class: {name}')
            annotation = notes[name]
            fields = {f['key']: f for f in meta['fields']}
            highlights = []
            for h in annotation['highlights']:
                missing = set(h['keys']) - fields.keys()
                if missing:
                    errors.append(f'{name}: {sorted(missing)}')
                else:
                    highlights.append({**h, 'fields': [expand(fields[k]) for k in h['keys']]})
            nodes.append({**meta, **annotation, 'highlights': highlights, 'category': group['id'],
                'rank': order.index(name) + 1, 'fields': [expand(f) for f in meta['fields']]})
    if errors:
        raise ValueError('Unknown highlighted fields:\n' + '\n'.join(errors))
    by_name = {n['name']: n for n in nodes}
    def evidence(filename, needle):
        paths = list(repo.glob('Source/**/' + filename))
        if len(paths) != 1:
            raise ValueError(f'Evidence file ambiguous/missing: {filename}')
        path = paths[0].relative_to(repo).as_posix()
        lines = paths[0].read_text(encoding='utf-8-sig').splitlines()
        hits = [i+1 for i,l in enumerate(lines) if needle in l and not l.lstrip().startswith('#include')]
        if not hits:
            raise ValueError(f'Evidence missing: {filename}: {needle}')
        return dict(path=path, line=hits[0], url=url(path,hits[0]), snippet=lines[hits[0]-1].strip())
    spec = runpy.run_path(str(HERE / 'core-class-flows.py'))
    manual, edges = spec['relationships'](), {}
    def resolve_edge(a, b):
        key = a + '>' + b
        if key in edges:
            return key
        left, right = by_name[a], by_name[b]
        if key in manual:
            e = manual[key]
            edges[key] = {**e, 'source':a, 'target':b, 'id':key, 'evidence':evidence(e['file'],e['needle'])}
        elif b in left['bases']:
            edges[key] = dict(id=key,source=a,target=b,kind='inheritance',label='상속',payload='공통 상태와 기능 재사용',
                detail=f'{a}는 {b}를 상속합니다. 추가 필드와 부모의 상태를 함께 읽습니다.',
                evidence=dict(path=left['path'],line=left['line'],url=left['url'],snippet=texts[left['path']].splitlines()[left['line']-1].strip()))
        else:
            candidates = []
            def find_refs(field, trail, root):
                if b in field['references']:
                    candidates.append((field, trail+field['key'], root))
                for s in field['schemas']:
                    for f in s['fields']:
                        find_refs(f,trail+field['key']+' → '+s['name']+'.',root)
            for f in left['fields']:
                find_refs(f,'',f['key'])
            if not candidates:
                raise ValueError(f'No field/inheritance evidence; add reviewed runtime relation: {key}')
            highlighted = [k for h in left['highlights'] for k in h['keys']]
            candidates.sort(key=lambda c:(c[1].count(' → '),highlighted.index(c[2]) if c[2] in highlighted else 999))
            f, trail, root = candidates[0]
            meaning = next((h['meaning'] for h in left['highlights'] if root in h['keys']),right['role'])
            config = right['storage'] == '설정 Data Asset'
            edges[key] = dict(id=key,source=a,target=b,kind='config' if config else 'reference',
                label='설정 참조' if config else '참조 보관',payload=trail if ' → ' not in trail else trail.split(' → ')[0]+' → '+trail.split('.')[-1],
                detail=f'{trail}: {meaning}. {right["purpose"]}',
                evidence={k:f[k] for k in ('path','line','url')} | {'snippet':f['declaration']})
        return key
    for g in groups:
        g['intro'], g['flows'] = spec['INTROS'][g['id']], []
        for title, explanation, names in spec['FLOWS'][g['id']]:
            pairs = [resolve_edge(a,b) for a,b in zip(names,names[1:])]
            g['flows'].append(dict(title=title,explanation=explanation,nodes=names,edges=pairs))
        covered = {n for f in g['flows'] for n in f['nodes']}
        if set(g['names']) - covered:
            raise ValueError(f'Classes missing from {g["id"]}: {set(g["names"]) - covered}')
    for key in manual:
        resolve_edge(*key.split('>'))
    # The focused diagram also exposes direct data dependencies between the 100 classes.
    # Curated system lanes remain small; there is no all-class hairball view.
    def field_references(f):
        yield from f['references']
        for schema in f['schemas']:
            for child in schema['fields']:
                yield from field_references(child)
    for n in nodes:
        targets = set(n['bases']) & set(selected)
        targets.update(t for f in n['fields'] for t in field_references(f))
        for target in sorted(targets - {n['name']}):
            resolve_edge(n['name'],target)
    nodes.sort(key=lambda n:n['rank'])
    result = dict(meta=dict(commit=sha,sourceDate=git('show','-s','--format=%cI','HEAD'),
        classCount=len(nodes),relationshipCount=len(edges),categoryCount=len(groups)),categories=groups,nodes=nodes,edges=list(edges.values()))
    destination = HERE.parent / 'pandora-battle-portfolio'
    (destination/'assets/class-map-data.js').write_text('window.PANDORA_CLASS_MAP = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8',newline='\n')
    rows = []
    for n in nodes:
        rows.append(f'<li><a href="{html.escape(n["url"])}" target="_blank" rel="noopener noreferrer">#{n["rank"]:03d} {n["name"]} ↗</a><b>{html.escape(n["role"])}</b><p>{html.escape(n["purpose"])}</p><a href="class-map.html?v=core100-1&amp;class={n["name"]}">데이터와 관계 보기 →</a></li>')
    page = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pandora Battle · 핵심 100 클래스</title><link rel="stylesheet" href="assets/class-map.css?v=core100-1"></head><body><main class="source-index"><a href="class-map.html?v=core100-1">← 핵심 클래스 관계도</a><h1>핵심 클래스 100</h1><p>구조 이해를 위한 읽기 우선순위입니다. 설정·실행 상태·영구 저장·표시 데이터를 구분했습니다.</p><ol>'+''.join(rows)+'</ol></main></body></html>\n'
    (destination/'class-index.html').write_text(page,encoding='utf8',newline='\n')
    print(f'Built {len(nodes)} classes / {len(edges)} explained relationships / {len(groups)} systems at {sha[:8]}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo',type=Path)
    build(parser.parse_args().repo.resolve())
