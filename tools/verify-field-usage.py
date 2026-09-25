"""Regression checks for direct C++ member use, Getter paths and pinned evidence."""
import argparse
import json
from pathlib import Path
import re
import runpy
import tempfile

HERE=Path(__file__).resolve().parent
Index=runpy.run_path(str(HERE/'build-field-usage.py'))['Index']


def fixtures():
    code='''
class Data { public: int Value; };
class Other { public: int Value; };
class Owner {
public:
 int Value;
 Data* Record;
 static int StaticValue;
 int GetValue() const { return Value; }
 void Indirect() { GetValue(); }
 void SetValue(int NewValue) { Value=NewValue; }
 void SetIndirect() { SetValue(1); }
 void Shadow(int Value) { Use(Value); }
 void LocalShadow() { int Value=1; Use(Value); }
 void Explicit(int Value) { this->Value=Value; }
 void External(Data* D) { Use(D->Value); }
 void Different(Other* D) { Use(D->Value); }
 void LambdaShadow() { auto Fn=[Value=1](){ return Value; }; }
 void LambdaMember() { auto Fn=[this](){ return Value; }; }
 void StaticRead() { Use(Owner::StaticValue); }
 void CommentOnly() { /* Value */ Use("Value"); }
 void LocalClass() { class Helper { int Value; int Get() { return Value; } }; }
 Owner(): Value(1) {}
};
'''
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);(root/'fixture.h').write_text(code,encoding='utf-8')
        index=Index(root,'test');index.read(['fixture.h'])
        uses={f['name']:index.analyze(f) for f in index.functions if f['owner']=='Owner'}
        for name in ('Indirect','SetIndirect','Shadow','LocalShadow','LambdaShadow','CommentOnly','LocalClass'):
            assert not uses[name],(name,uses[name])
        assert ('Owner','Value') in uses['GetValue']
        assert ('Owner','Value') in uses['Explicit']
        assert ('Owner','Value') in uses['LambdaMember']
        assert ('Owner','Value') in uses['Owner']
        assert ('Data','Value') in uses['External'] and ('Owner','Value') not in uses['External']
        assert ('Other','Value') in uses['Different'] and ('Data','Value') not in uses['Different']
        assert ('Owner','StaticValue') in uses['StaticRead']
        index.index_getters()
        by_name={f['name']:f for f in index.functions if f['owner']=='Owner'}
        indirect=index.analyze(by_name['Indirect'],True)
        assert indirect['Owner','Value'][0]['via']=='Owner::GetValue()'
        assert not index.analyze(by_name['SetIndirect'],True)


def verify(repo):
    fixtures()
    site=HERE.parent/'pandora-battle-portfolio/assets'
    def load(file):
        return json.loads((site/file).read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))
    data,atlas=load('field-usage-data.js'),load('class-map-data.js')
    assert data['meta']['commit']==atlas['meta']['commit']
    classes={n['name']:n for n in atlas['nodes']}
    assert set(classes)==set(data['classes'])
    sources={}
    def lines(path):
        assert path.startswith('Source/') and '..' not in path
        if path not in sources:sources[path]=(repo/path).read_text(encoding='utf-8-sig').splitlines()
        return sources[path]
    checks=0
    for owner,fields in data['classes'].items():
        assert set(fields)=={f['key'] for f in classes[owner]['fields']}
        for key,doc in fields.items():
            assert doc['purpose'].strip() and (len(doc['purpose'])>15 or doc['purposeBasis']=='source-comment'),(owner,key)
            ids=[u['function'] for u in doc['uses']];assert len(ids)==len(set(ids))
            for use in doc['uses']:
                fn=data['functions'][use['function']]
                name_pattern = (r'\boperator\s*'+re.escape(fn['name'][8:])) if fn['name'].startswith('operator') else r'(?<!\w)'+re.escape(fn['name'])+r'(?!\w)'
                assert re.search(name_pattern, '\n'.join(lines(fn['path'])[fn['line']-1:fn['line']+8])) or fn['generated'],fn
                assert fn['url'].endswith('#L'+str(fn['line'])) and data['meta']['commit'] in fn['url']
                assert use['access'] in ('direct','getter')
                for hit in use['evidence']:
                    checks+=1
                    assert lines(fn['path'])[hit['line']-1].strip()==hit['snippet']
                    if hit['via'] and not fn['generated']:
                        getter=data['getters'][hit['via']]
                        assert getter['name'].startswith('Get')
                        assert re.search(r'\b'+re.escape(getter['name'])+r'\b',hit['snippet'])
                        member=next(m for m in getter['members'] if m['owner']==owner and m['key']==key)
                        assert any(re.search(r'\b'+re.escape(key)+r'\b',lines(getter['path'])[line-1]) for line in member['lines'])
                    else:
                        assert re.search(r'\b'+re.escape(key)+r'\b',hit['snippet']),(owner,key,fn,hit)
                assert use['access']=='direct' if fn['generated'] or any(not h['via'] for h in use['evidence']) else use['access']=='getter'
    def names(owner,key):return {data['functions'][u['function']]['owner']+'::'+data['functions'][u['function']]['name'] for u in data['classes'][owner][key]['uses']}
    assert 'APdPlayerState::GetAbilitySystemComponent' in names('APdPlayerState','AbilitySystemComponent')
    assert 'APdPlayer::GetAbilitySystemComponent' in names('APdPlayerState','AbilitySystemComponent')
    assert 'USkillAbility::PreActivate' in names('UPandoraSkillSource','PandoraDefinition')
    ability_use=next(u for u in data['classes']['UPandoraSkillSource']['PandoraDefinition']['uses'] if data['functions'][u['function']]['owner']=='USkillAbility' and data['functions'][u['function']]['name']=='PreActivate')
    assert ability_use['access']=='getter' and 'UPandoraSkillSource::GetPandoraDefinition()' in ability_use['via']
    assert 'UPandoraSkillSource::Initialize' in names('UPandoraSkillSource','PandoraDefinition')
    assert 'FPandoraSkillBinder::GrantPandoraContent' in names('UPandoraDefinition','Skills')
    assert 'UPandoraTreeComponent::ArePandoraUnlockRulesMet' in names('UPandoraDefinition','UnlockRules')
    assert 'UPandoraDefinition::GetMaxLevel' in names('UPandoraDefinition','MaxLevel')
    assert 'UPandoraSkillSource::GetSkillDataAsset' in names('UPandoraDefinition','Skills')
    assert 'USkillAbility::ActivateAbility' in names('USkillDefinition','Action')
    assert 'USkillAbility::GetRemainingDuration' in names('USkillAbility','DurationEndTime')
    assert 'USkillRepeatAction::RunNext' in names('USkillRepeatAction','Action')
    assert 'UStatUpgradeDefinition::CalculateInitialAttributeValues' in names('UStatUpgradeDefinition','AttributeDefaultValues')
    assert 'UBasicAttributeSet::CalculateCooldownDuration' in names('UBasicAttributeSet','Arcane')
    assert 'UReactiveStatusEffectAbility::OnGameplayEffectAppliedToTarget' in names('UStatusEffectDefinition','StackTag')
    assert not data['classes']['ULobbyRuntimeSubsystem']['bLobbyDataAssetsReady']['uses']
    print(json.dumps({'result':'PASS','classes':len(classes),'members':data['meta']['fields'],'functions':len(data['functions']),'sourceEvidenceChecks':checks,'getterPaths':'verified separately','setterOnlyCallers':'excluded','scopeFixtures':14}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('repo',type=Path)
    verify(parser.parse_args().repo.resolve())
