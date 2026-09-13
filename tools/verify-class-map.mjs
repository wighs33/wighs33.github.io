import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(process.argv[2] || '../pandora-class-source');
const site=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../pandora-battle-portfolio');
const sandbox={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(site,'assets/class-map-data.js'),'utf8'),sandbox);
const data=JSON.parse(JSON.stringify(sandbox.window.PANDORA_CLASS_MAP));
const nodes=new Map(data.nodes.map(n=>[n.name,n]));
const edges=new Map(data.edges.map(e=>[e.id,e]));
const sourceFiles=new Map();
const sha=execFileSync('git',['-C',repo,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
assert.equal(data.meta.commit,sha,'Source snapshot must match the linked commit');
assert.equal(nodes.size,100);assert.equal(data.nodes.length,100);assert.equal(data.meta.classCount,100);
assert.equal(data.categories.length,9);assert.equal(data.meta.relationshipCount,edges.size);
assert.deepEqual(data.nodes.map(n=>n.rank),Array.from({length:100},(_,i)=>i+1));
const normalize=s=>s.replace(/\s+/g,' ').trim();
function source(p){
  assert(p.startsWith('Source/')&&!p.includes('..'),'Source path stays inside the game source');
  if(!sourceFiles.has(p))sourceFiles.set(p,fs.readFileSync(path.join(repo,p),'utf8').replace(/^\uFEFF/,'').split(/\r?\n/));
  return sourceFiles.get(p);
}
function verifyLink(record){
  assert(Number.isInteger(record.line)&&record.line>0);
  assert(record.line<=source(record.path).length);
  assert.equal(record.url,`https://github.com/wighs33/Pandora-Battle/blob/${sha}/${encodeURI(record.path)}#L${record.line}`);
}
let fields=0,schemas=0;
function verifyField(f){
  verifyLink(f);fields++;
  assert(normalize(source(f.path).slice(f.line-1).join('\n')).startsWith(f.declaration),`Field differs from actual source: ${f.path}:${f.line} ${f.key}`);
  assert(new RegExp(`\\b${f.key}\\b`).test(f.declaration));
  f.references.forEach(name=>assert(nodes.has(name)));
  f.schemas.forEach(s=>{
    verifyLink(s);schemas++;
    assert(source(s.path)[s.line-1].includes(s.name),`Nested schema declaration mismatch: ${s.name}`);
    s.fields.forEach(verifyField);
  });
}
for(const n of data.nodes){
  assert.equal(n.kind,'class');assert.equal(n.parseError,false);assert(n.path.endsWith('.h'));
  assert(n.role&&n.purpose&&n.storage);verifyLink(n);
  assert(source(n.path)[n.line-1].includes(n.name),`Class declaration mismatch: ${n.name}`);
  assert.equal(n.fields.length,new Set(n.fields.map(f=>f.key)).size);
  n.fields.forEach(verifyField);
  for(const h of n.highlights){assert(h.meaning.length>4);assert.deepEqual(h.keys,h.fields.map(f=>f.key));h.fields.forEach(verifyField);}
  assert(n.highlights.length>0||n.fields.length===0,`Missing data explanation: ${n.name}`);
  assert(data.edges.some(e=>e.source===n.name||e.target===n.name),`Unconnected selected class: ${n.name}`);
}
assert.equal(edges.size,data.edges.length,'No duplicate directional relationships');
for(const e of data.edges){
  assert(nodes.has(e.source)&&nodes.has(e.target));assert.notEqual(e.source,e.target);
  assert(e.label&&e.payload&&e.detail);verifyLink(e.evidence);
  assert(normalize(source(e.evidence.path).slice(e.evidence.line-1).join('\n')).startsWith(normalize(e.evidence.snippet)),`Relation evidence mismatch: ${e.id}`);
}
const classified=[];
let lanes=0;
for(const c of data.categories){
  assert(c.intro);classified.push(...c.names);
  const covered=new Set();
  for(const f of c.flows){
    lanes++;assert(f.title&&f.explanation);assert(f.nodes.length>=2&&f.nodes.length<=3);assert.equal(f.edges.length,f.nodes.length-1);
    f.nodes.forEach(n=>{assert(nodes.has(n));covered.add(n);});
    f.edges.forEach((id,i)=>{const e=edges.get(id);assert(e);assert.equal(e.source,f.nodes[i]);assert.equal(e.target,f.nodes[i+1]);});
  }
  c.names.forEach(n=>{assert.equal(nodes.get(n).category,c.id);assert(covered.has(n),`Class omitted from its system diagram: ${n}`);});
}
assert.equal(classified.length,100);assert.equal(new Set(classified).size,100);
// Regression: a source object is not player ownership, tree level, or permanent storage.
assert(!nodes.get('APdPlayerState').fields.some(f=>f.references.includes('UPandoraSkillSource')));
assert.deepEqual(nodes.get('UPandoraInstance').fields.map(f=>f.key),['PandoraDefinition','IsOwned']);
assert(nodes.get('UPandoraTreeComponent').fields.find(f=>f.key==='GrantedPandoras').schemas[0].fields.some(f=>f.key==='Level'));
assert(nodes.get('UPandoraDefinition').fields.find(f=>f.key==='Skill').schemas[0].fields.some(f=>f.key==='SkillDefinition'&&f.references.includes('USkillDefinition')));
assert(nodes.get('USkillDefinition').fields.find(f=>f.key==='Time').schemas[0].fields.some(f=>f.key==='CooldownDuration'));
assert(nodes.get('UPdSaveGame').fields.find(f=>f.key==='PlayerPandoraData').schemas[0].fields.some(f=>f.key==='GrantedPandorasById'&&f.declaration.includes('FPrimaryAssetId')));
for(const id of ['APdPlayerState>UPandoraComponent','UPandoraComponent>UPandoraDefinition','UPandoraDefinition>USkillDefinition','FPandoraSkillBinder>UPandoraSkillSource','FPandoraSkillBinder>UPdAbilitySystemComponent','UPdAbilitySystemComponent>UPandoraSkillSource','UPdGameplayAbility>UPandoraSkillSource'])assert(edges.has(id),`Missing Pandora path: ${id}`);
assert.equal(edges.get('UPandoraDefinition>UPandoraDescriptionViewModel').kind,'projection');
assert.equal(edges.get('UGameFeatureAction_AddAbilities>UGameFeatureAction_AddActorExtension').kind,'sequence');
assert(!edges.has('AMonsterAIController>UBTTask_EnemyAttack'),'StateTree and BT must remain distinct');
const index=fs.readFileSync(path.join(site,'class-index.html'),'utf8');
assert.equal((index.match(/https:\/\/github.com\/wighs33\/Pandora-Battle\/blob\//g)||[]).length,100);
for(const name of fs.readdirSync(site).filter(n=>n.endsWith('.html'))){
  const html=fs.readFileSync(path.join(site,name),'utf8');
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size,`Duplicate id: ${name}`);
  for(const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
    const ref=match[1];if(/^[a-z]+:|^\/\//i.test(ref))continue;
    const [pathname,anchor]=ref.split('#');const target=path.resolve(site,pathname.split('?')[0]||name);
    assert(fs.existsSync(target),`Missing local link ${name}: ${ref}`);
    if(anchor&&target.endsWith('.html'))assert(fs.readFileSync(target,'utf8').includes(`id="${anchor}"`),`Missing anchor ${name}: ${ref}`);
  }
}
const markup=fs.readFileSync(path.join(site,'class-map.html'),'utf8'),script=fs.readFileSync(path.join(site,'assets/class-map.js'),'utf8');
for(const [,id] of script.matchAll(/\$\('([^']+)'\)/g))assert(markup.includes(`id="${id}"`),`JS references a missing element: ${id}`);
assert(!/576 TYPES|341개|235개/.test(fs.readFileSync(path.join(site,'index.html'),'utf8')));
console.log(JSON.stringify({result:'PASS',classes:nodes.size,systems:data.categories.length,diagramFlows:lanes,relationships:edges.size,fieldChecks:fields,nestedSchemas:schemas,sourceFiles:sourceFiles.size,commit:sha},null,2));
