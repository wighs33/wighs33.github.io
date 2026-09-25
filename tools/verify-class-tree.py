"""Check complete header coverage, exact declarations, and corrected pasted-tree relationships."""
import argparse
import json
from pathlib import Path
import re
import runpy
import subprocess

HERE=Path(__file__).resolve().parent
P=runpy.run_path(str(HERE/'cpp-schema.py'))


def verify(repo):
    site=HERE.parent/'pandora-battle-portfolio'
    data=json.loads((site/'assets/class-map-data.js').read_text(encoding='utf8').split(' = ',1)[1].rstrip(';\n'))
    sha=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],encoding='utf8').strip()
    assert data['meta']['commit']==sha
    nodes={n['name']:n for n in data['nodes']}
    assert len(nodes)==len(data['nodes'])
    # Independent declaration scan catches omitted headers and definitions.
    expected=set()
    for path in (repo/'Source/LabProject').rglob('*.h'):
        clean=P['sanitize'](path.read_bytes())
        for m in re.finditer(rb'\b(?:class|struct|union)\s+([A-Za-z_]\w*(?:\s*<[^<>;{}]+>)?)\s*(?:final\s*)?(?:\:[^;{}]*)?\{',clean):
            if not re.search(rb'\benum\s+$',clean[:m.start()]):
                expected.add(re.sub(r'\s+','',m[1].decode()))
    declared={n['name'] for n in nodes.values() if n['kind'] in ('class','struct','union')}
    assert expected==declared,dict(missing=sorted(expected-declared),unexpected=sorted(declared-expected))
    source={}
    def content(path):
        assert path.startswith('Source/LabProject/') and '..' not in path
        if path not in source:source[path]=(repo/path).read_text(encoding='utf-8-sig').splitlines()
        return source[path]
    fields=methods=0
    for n in nodes.values():
        assert n['name'] in content(n['path'])[n['line']-1]
        assert sha in n['url'] and n['url'].endswith('#L'+str(n['line']))
        assert n['name'] not in n['bases'],n['name']
        assert n['purpose'].strip()
        assert n['folder']==str(Path(n['path']).parent).replace('\\','/').removeprefix('Source/LabProject').strip('/')
        assert len({f['key'] for f in n['fields']})==len(n['fields'])
        for declaration in n['fields']+n['methods']:
            lines=content(declaration['path'])
            raw=' '.join(lines[declaration['line']-1:declaration['line']+40])
            assert re.sub(r'\s+','',declaration['declaration']) in re.sub(r'\s+','',raw),(n['name'],declaration)
            assert sha in declaration['url']
        fields+=len(n['fields']);methods+=len(n['methods'])
    for name,parent in [('AMeleeWeapon','AWeaponBase'),('ARangedWeaponBase','AWeaponBase'),('ABow','ARangedWeaponBase'),('AGun','ARangedWeaponBase'),('AMonsterCharacter','AEnemyBase'),('UAnimNotify_RedrawBow','UAnimNotify_WeaponEvent'),('UPlayerHudWidget','ULocalizedMenuWidget')]:
        assert nodes[name]['bases'][0]==parent,(name,parent)
    for absent in ('UPandoraSkillBinder','USkillActions','ASword','FStateTree_PdUtilityTasks','UWidgetContentBundle'):
        assert absent not in nodes
    assert nodes['FPandoraSkillBinder']['kind']=='class'
    assert nodes['PdCharacterHitValidation']['kind']=='namespace'
    assert nodes['EWidgetContentBundle']['kind']=='enum'
    assert nodes['FWidgetContentBundleLease']['bases']==['TSharedFromThis']
    assert {f['key'] for f in nodes['UPandoraSkillSource']['fields']}=={'PandoraDefinition','SkillIndex','LoadoutDirection'}
    assert 'OwnedSkillSources' in {f['key'] for f in nodes['UPandoraComponent']['fields']}
    assert not {'GrantedPandoraSkillSources','ActivationsWaitingForSource'} & {f['key'] for f in nodes['UPdAbilitySystemComponent']['fields']}
    for file in ('class-map.html','index.html','class-index.html','assets/class-map.js'):
        text=(site/file).read_text(encoding='utf8')
        assert not re.search(r'핵심\s*100|선정 기준|class-graph-model|graph-world|CORE CLASSES',text),file
    print(json.dumps(dict(result='PASS',classes=data['meta']['counts']['class'],declarations=len(nodes),fields=fields,methods=methods,headers=len(source),commit=sha)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('repo',type=Path)
    verify(parser.parse_args().repo.resolve())
