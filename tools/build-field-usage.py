"""Source-backed member usage index for the curated C++ atlas (no token search matches)."""
import argparse
import collections
import json
from pathlib import Path
import re
import runpy
import subprocess
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'cpp-schema.py'))
walk, text = P['walk'], P['text']


def named_declarator(node):
    while node:
        child = node.child_by_field_name('declarator')
        if child is None and node.type in ('reference_declarator', 'pointer_declarator'):
            child = next((c for c in node.named_children if c.type not in ('type_qualifier',)), None)
        if child is None:
            return node
        node = child


def preceding_comment(raw, row):
    lines = raw.decode('utf-8-sig').splitlines()
    i, out = row - 1, []
    # Field annotations may occupy several lines between a comment and declaration.
    if i >= 0 and (lines[i].lstrip().startswith('UPROPERTY') or 'meta =' in lines[i] or lines[i].strip().endswith('))')):
        while i >= 0 and not lines[i].lstrip().startswith('UPROPERTY'):
            i -= 1
        i -= 1
    while i >= 0:
        s = lines[i].strip()
        if s.startswith(('//', '/*', '*')):
            s = re.sub(r'^[/\s*]+|[\s*/]+$', '', s)
            if s and not re.fullmatch(r'[-=]+', s):
                out.insert(0, s)
            i -= 1
        else:
            break
    result = ' '.join(out)
    return result if re.search('[가-힣]', result) and len(result) > 8 else ''


class Index:
    def __init__(self, repo, sha):
        self.repo, self.sha = repo, sha
        self.types, self.functions, self.sources, self.asts = {}, [], {}, {}
        self.method_types = {}
        self.getters = {}
        self.unresolved = collections.Counter()

    def link(self, path, line):
        return f'https://github.com/wighs33/Pandora-Battle/blob/{self.sha}/' + quote(path, safe='/') + '#L' + str(line)

    def type_text(self, node):
        return text(node.child_by_field_name('type'))

    def type_name(self, raw):
        names = re.findall(r'\b[A-Za-z_]\w*\b', raw)
        return next((n for n in names if n in self.types), '')

    def field(self, owner, key, seen=()):
        if owner in seen:
            return None
        info = self.types.get(owner, {})
        if key in info.get('fields', {}):
            return owner, info['fields'][key]
        for base in info.get('bases', []):
            found = self.field(base, key, seen + (owner,))
            if found:
                return found
        return None

    def method_type(self, owner, name, seen=()):
        if owner in seen:
            return ''
        if (owner, name) in self.method_types:
            return self.method_types[owner, name]
        for base in self.types.get(owner, {}).get('bases', []):
            found = self.method_type(base, name, seen + (owner,))
            if found:
                return found
        return ''

    def getter(self, owner, name, seen=()):
        if owner in seen or not name.startswith('Get'):
            return None
        if (owner,name) in self.getters:
            return self.getters[owner,name]
        for base in self.types.get(owner,{}).get('bases',[]):
            found=self.getter(base,name,seen+(owner,))
            if found:return found
        return None

    def index_getters(self):
        for f in self.functions:
            if not f['name'].startswith('Get') or f.get('returnType')=='void':
                continue
            if f.get('macro'):
                members=[{'owner':f['owner'],'key':f['key'],'mode':f['mode'],'lines':[f['line']]}]
            else:
                refs=self.analyze(f,False)
                members=[{'owner':owner,'key':key,'mode':'read','lines':sorted({h['line'] for h in hits})}
                    for (owner,key),hits in refs.items() if self.field(f['owner'],key) and self.field(f['owner'],key)[0]==owner]
            if members:
                self.getters[f['owner'],f['name']]={k:f[k] for k in ('owner','name','path','line','url')}|{'members':members,'generated':bool(f.get('macro'))}

    def read(self, paths):
        for path in paths:
            if not path.endswith(('.h', '.cpp')):
                continue
            raw = (self.repo / path).read_bytes()
            root = P['PARSER'].parse(P['sanitize'](raw)).root_node
            self.sources[path], self.asts[path] = raw, root
            for n in walk(root):
                if n.type not in P['DEFINITION_TYPES'] or not n.child_by_field_name('body'):
                    continue
                name = text(n.child_by_field_name('name'))
                if not name:
                    continue
                fields = {}
                for member in n.child_by_field_name('body').named_children:
                    if member.type not in ('field_declaration', 'declaration') or any(c.type == 'function_declarator' for c in walk(member)):
                        continue
                    decl = named_declarator(member.child_by_field_name('declarator'))
                    if decl:
                        fields[text(decl)] = {'type':self.type_text(member), 'node':member, 'path':path}
                bases = next((c for c in n.named_children if c.type == 'base_class_clause'), None)
                self.types[name] = {'fields':fields, 'bases':[x[0] for x in P['declared_types'](bases)]}
        # All type names must be known before resolving return types and external receivers.
        for path, root in self.asts.items():
            for n in walk(root):
                if n.type not in ('function_definition', 'field_declaration', 'declaration'):
                    continue
                declarator = n.child_by_field_name('declarator')
                if declarator is None:
                    continue
                fn = next((c for c in walk(declarator) if c.type == 'function_declarator'), None)
                if fn is None:
                    continue
                d = named_declarator(fn)
                qualified = re.sub(r'\s+', '', text(d))
                if '::' in qualified:
                    owner, name = qualified.rsplit('::', 1)
                else:
                    parent = n.parent
                    while parent and parent.type not in P['DEFINITION_TYPES']:
                        parent = parent.parent
                    owner = text(parent.child_by_field_name('name')) if parent else ''
                    name = qualified
                ret = self.type_text(n)
                if owner in self.types:
                    self.method_types[owner, name] = ret
                if n.type != 'function_definition':
                    continue
                body = n.child_by_field_name('body')
                if not body:
                    continue
                line = n.start_point.row + 1
                self.functions.append({'owner':owner, 'name':name, 'path':path, 'line':line,
                    'url':self.link(path,line), 'comment':preceding_comment(self.sources[path],n.start_point.row),
                    'node':n, 'fn':fn, 'body':body, 'returnType':ret})
        # GAS's project-local ATTRIBUTE_ACCESSORS macro explicitly expands these four APIs.
        for path, raw in self.sources.items():
            if b'#define ATTRIBUTE_ACCESSORS' not in raw:
                continue
            for m in re.finditer(rb'ATTRIBUTE_ACCESSORS\((\w+),\s*(\w+)\)',raw):
                owner,key = (s.decode() for s in m.groups())
                if not self.field(owner,key):
                    continue
                for prefix,suffix,mode in [('Get','','read'),('Get','Attribute','attribute'),('Set','','write'),('Init','','write')]:
                    name = prefix+key+suffix
                    self.functions.append({'owner':owner,'name':name,'path':path,'line':raw[:m.start()].count(b'\n')+1,
                        'url':self.link(path,raw[:m.start()].count(b'\n')+1),'comment':'ATTRIBUTE_ACCESSORS 매크로가 생성하는 속성 접근 함수',
                        'macro':True,'key':key,'mode':mode})

    def scope_end(self, node, fn):
        parent = node.parent
        while parent and parent != fn:
            if parent.type in ('compound_statement','for_range_loop','for_statement','if_statement','lambda_expression'):
                return parent.end_byte
            parent = parent.parent
        return fn.end_byte

    def analyze(self, f, through_accessors=False):
        owner, fn, body = f['owner'], f['node'], f['body']
        def function_nodes(root):
            yield root
            for child in root.named_children:
                if child.type not in P['DEFINITION_TYPES'] | {'function_definition'}:
                    yield from function_nodes(child)
        locals_ = collections.defaultdict(list)
        for n in function_nodes(fn):
            if n.type == 'lambda_capture_initializer':
                left,right = n.child_by_field_name('left'),n.child_by_field_name('right')
                parent=n.parent
                while parent and parent.type!='lambda_expression':
                    parent=parent.parent
                if left and parent:
                    locals_[text(left)].append((parent.child_by_field_name('body').start_byte,parent.end_byte,'auto',right))
            if n.type not in ('parameter_declaration','optional_parameter_declaration','declaration','for_range_loop'):
                continue
            d = n.child_by_field_name('declarator')
            ident = named_declarator(d)
            if not ident or ident.type not in ('identifier','field_identifier'):
                continue
            value = d.child_by_field_name('value') if d else None
            typ = self.type_text(n)
            start = n.start_byte
            if n.type.endswith('parameter_declaration'):
                start = n.parent.start_byte
            locals_[text(ident)].append((start,self.scope_end(n,fn),typ,value))

        def local(name, position):
            candidates = [v for v in locals_.get(name,[]) if v[0]<=position<v[1]]
            return max(candidates,key=lambda v:v[0]) if candidates else None

        def resolve(expr, depth=0):
            if expr is None or depth>12:
                return ''
            typ, raw = expr.type, text(expr)
            if typ == 'this':
                return owner
            if typ == 'qualified_identifier':
                qualified = re.sub(r'\s+', '', raw)
                if '::' in qualified:
                    target,key = qualified.rsplit('::',1)
                    field = self.field(target,key)
                    return field[1]['type'] if field else ''
            if typ == 'identifier':
                entry = local(raw,expr.start_byte)
                if entry:
                    return entry[2] if entry[2] not in ('auto','') else resolve(entry[3],depth+1)
                field = self.field(owner,raw)
                return field[1]['type'] if field else ''
            if typ in ('pointer_expression','parenthesized_expression','subscript_expression'):
                return resolve(expr.child_by_field_name('argument') or expr.named_children[0],depth+1)
            if typ == 'field_expression':
                target = self.type_name(resolve(expr.child_by_field_name('argument'),depth+1))
                field = self.field(target,text(expr.child_by_field_name('field')))
                return field[1]['type'] if field else ''
            if typ == 'call_expression':
                callee = expr.child_by_field_name('function')
                if callee.type == 'template_function':
                    name = text(callee.child_by_field_name('name'))
                    args = callee.child_by_field_name('arguments')
                    if name.startswith(('Cast','Get','Find','NewObject','CreateDefaultSubobject','LoadObject')):
                        return text(args)
                if callee.type == 'field_expression':
                    receiver = resolve(callee.child_by_field_name('argument'),depth+1)
                    name = text(callee.child_by_field_name('field'))
                    if name in ('Get','GetDefaultObject','GetObject','LoadSynchronous','GetTypedOuter'):
                        return receiver
                    return self.method_type(self.type_name(receiver),name)
                if callee.type in ('identifier','qualified_identifier'):
                    name = text(callee)
                    target = owner
                    if '::' in name:
                        target,name = name.rsplit('::',1)
                    return self.method_type(target,name)
            if typ == 'conditional_expression':
                return resolve(expr.child_by_field_name('consequence'),depth+1) or resolve(expr.child_by_field_name('alternative'),depth+1)
            return ''

        found = collections.defaultdict(list)

        def mode(node):
            current = node
            while current.parent and current != body:
                parent = current.parent
                if parent.type == 'assignment_expression':
                    lhs = parent.child_by_field_name('left')
                    if lhs.start_byte<=node.start_byte<lhs.end_byte:
                        return 'write'
                if parent.type == 'update_expression':
                    return 'write'
                if parent.type == 'call_expression':
                    name = text(parent.child_by_field_name('function'))
                    if name.startswith('DOREPLIFETIME'):
                        return 'replication'
                    if name.startswith(('MARK_PROPERTY_DIRTY','GAMEPLAYATTRIBUTE_REPNOTIFY')):
                        return 'notification'
                    if parent.child_by_field_name('function').end_byte<=node.start_byte:
                        return 'argument'
                    if re.search(r'\.(?:Add\w*|Remove\w*|Reset|Empty|Set\w*|Append|Emplace\w*|FindOrAdd|Insert\w*|Sort|Reserve)\b',name):
                        return 'update'
                    return 'call'
                if parent.type == 'return_statement':
                    return 'return'
                if parent.type in ('expression_statement','declaration','if_statement'):
                    break
                current = parent
            return 'read'

        def add(target,key,node,via='',access=None):
            field = self.field(target,key)
            if not field:
                return
            declared_owner = field[0]
            row = node.start_point.row+1
            snippet = self.sources[f['path']].decode('utf-8-sig').splitlines()[row-1].strip()
            found[declared_owner,key].append({'line':row,'mode':access or mode(node),'via':via,'snippet':snippet})

        for n in function_nodes(body):
            if n.type == 'field_expression':
                key = text(n.child_by_field_name('field'))
                receiver = self.type_name(resolve(n.child_by_field_name('argument')))
                if self.field(receiver,key):
                    add(receiver,key,n.child_by_field_name('field'))
                elif not receiver and key:
                    self.unresolved[key]+=1
            elif n.type == 'qualified_identifier':
                qualified = re.sub(r'\s+', '', text(n))
                if '::' in qualified:
                    target,key = qualified.rsplit('::',1)
                    add(target,key,n)
            elif n.type == 'identifier':
                key = text(n)
                if local(key,n.start_byte) or not self.field(owner,key):
                    continue
                parent = n.parent
                if parent.type=='lambda_capture_initializer' and n==parent.child_by_field_name('left'):
                    continue
                if parent.type in ('qualified_identifier','field_expression','init_declarator','parameter_declaration') and n==parent.child_by_field_name('declarator'):
                    continue
                if parent.type == 'qualified_identifier':
                    continue
                add(owner,key,n)
            elif n.type == 'call_expression' and through_accessors:
                callee = n.child_by_field_name('function')
                if callee.type == 'field_expression':
                    target = self.type_name(resolve(callee.child_by_field_name('argument')))
                    name = text(callee.child_by_field_name('field'))
                elif callee.type == 'identifier':
                    target,name = owner,text(callee)
                else:
                    continue
                getter=self.getter(target,name)
                if getter:
                    for member in getter['members']:
                        add(member['owner'],member['key'],callee.child_by_field_name('field') or callee,getter['owner']+'::'+getter['name']+'()',member['mode'])
        # Constructor member-initializer lists occur before the compound body.
        for n in fn.named_children:
            if n.type != 'field_initializer_list':
                continue
            for init in n.named_children:
                if init.type == 'field_initializer' and init.named_children:
                    key = text(init.named_children[0])
                    add(owner,key,init,access='write')
        return found


def build(repo, destination=None):
    git = lambda *args:subprocess.check_output(['git','-C',str(repo),*args],encoding='utf-8').strip()
    if git('status','--porcelain'):
        raise ValueError('Source checkout must be clean')
    sha = git('rev-parse','HEAD')
    site = HERE.parent/'pandora-battle-portfolio'
    data = json.loads((site/'assets/class-map-data.js').read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))
    assert data['meta']['commit']==sha
    index = Index(repo,sha)
    index.read(git('ls-files','Source').splitlines())
    index.index_getters()
    selected = {n['name']:n for n in data['nodes']}
    uses = collections.defaultdict(list)
    functions = {}
    for f in index.functions:
        fid = f['path']+':'+str(f['line'])+':'+f['name']
        if f.get('macro'):
            raw = index.sources[f['path']].decode('utf-8-sig').splitlines()[f['line']-1].strip()
            refs = {(f['owner'],f['key']):[{'line':f['line'],'mode':f['mode'],'via':'ATTRIBUTE_ACCESSORS','snippet':raw}]}
        else:
            # Keep direct references and one verified Getter hop distinguishable.
            # Setter-only callers and arbitrary transitive callers are not indexed.
            refs = index.analyze(f,True)
        for (owner,key),hits in refs.items():
            if owner not in selected or key not in {x['key'] for x in selected[owner]['fields']}:
                continue
            functions[fid] = {k:f.get(k,'') for k in ('owner','name','path','line','url','comment')}
            functions[fid]['generated'] = bool(f.get('macro'))
            functions[fid]['context'] = 'test' if '/Tests/' in f['path'] else 'editor' if 'Editor/' in f['path'] or f['name'].startswith(('Validate','IsDataValid','PostEdit')) else 'runtime'
            unique = {(h['line'],h['mode'],h['via']):h for h in hits}
            uses[owner,key].append({'function':fid,'modes':sorted({h['mode'] for h in hits}),
                'access':'direct' if f.get('macro') or any(not h['via'] for h in hits) else 'getter',
                'via':sorted({h['via'] for h in hits if h['via']}),'evidence':list(unique.values())})
    fields = {}
    describe = runpy.run_path(str(HERE/'field-usage-content.py'))['purpose']
    for owner,n in selected.items():
        fields[owner] = {}
        for field in n['fields']:
            key = field['key']
            h = next((h for h in n['highlights'] if key in h['keys']),None)
            comment = preceding_comment(index.sources[field['path']],field['line']-1)
            refs = uses[owner,key]
            refs.sort(key=lambda u:(functions[u['function']]['owner']!=owner,functions[u['function']]['generated'],functions[u['function']]['name'],u['function']))
            doc = {'meaning':h['meaning'] if h else '', 'comment':comment, 'uses':refs}
            doc['purpose'],doc['purposeBasis'] = describe(n,field,doc,functions,selected)
            fields[owner][key] = doc
    result = {'meta':{'commit':sha,'classes':len(selected),'fields':sum(map(len,fields.values())),
        'sourceFiles':len(index.sources),'functions':len(functions)},'functions':functions,'classes':fields,
        'getters':{owner+'::'+name+'()':g for (owner,name),g in index.getters.items()}}
    target = destination or site/'assets/field-usage-data.js'
    target.write_text('window.PANDORA_FIELD_USAGE = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['meta']))
    print('Fields without recognized C++ uses:',sum(not f['uses'] for group in fields.values() for f in group.values()))
    return result,index


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('repo',type=Path)
    args=parser.parse_args()
    build(args.repo.resolve())
