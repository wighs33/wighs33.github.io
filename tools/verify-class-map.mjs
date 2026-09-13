import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(process.argv[2]||'../pandora-class-source');
const site=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../pandora-battle-portfolio');
const sandbox={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(site,'assets/class-map-data.js'),'utf8'),sandbox);
const data=sandbox.window.PANDORA_CLASS_MAP,ids=new Map(data.nodes.map(n=>[n.id,n]));
assert.equal(ids.size,data.nodes.length,'Node IDs must be unique');
assert.equal(data.meta.classes,data.nodes.filter(n=>n.kind==='class').length);
assert.equal(data.meta.structs,data.nodes.filter(n=>n.kind==='struct').length);
const sourceFiles=new Map();
for(const node of data.nodes){
  const file=path.join(repo,node.path);
  assert(fs.existsSync(file),`Missing source ${node.path}`);
  if(!sourceFiles.has(file))sourceFiles.set(file,fs.readFileSync(file,'utf8').split(/\r?\n/));
  const line=sourceFiles.get(file)[node.line-1];
  assert(line?.includes(node.name),`Declaration line mismatch ${node.id}:${node.line}`);
  assert.equal(node.url,`https://github.com/${data.meta.repository}/blob/${data.meta.commit}/${node.path}#L${node.line}`);
  assert.equal(node.implementation,node.path.endsWith('.cpp'));
}
const edgeKeys=new Set();
for(const edge of data.edges){
  assert(ids.has(edge.source)&&ids.has(edge.target),'Edge endpoint missing');
  assert.notEqual(edge.source,edge.target,'Self edges should be omitted');
  const key=[edge.source,edge.target,edge.kind].join('|');
  assert(!edgeKeys.has(key),'Duplicate relation');edgeKeys.add(key);
  const file=path.join(repo,ids.get(edge.source).path);
  assert(sourceFiles.get(file)[edge.line-1]?.includes(ids.get(edge.target).name),'Relation must cite a real declaration line');
}
for(const [source,target,kind] of [
  ['AEnemyBase','ACharacterBase','inheritance'],
  ['APdPlayerState','UInventoryComponent','member'],
  ['APdPlayerState','UPdAbilitySystemComponent','member'],
  ['APdPlayerState','UInventoryComponent','signature'],
  ['FReplicatedInventoryList','FReplicatedInventoryEntry','member'],
]){
  assert(data.edges.some(e=>ids.get(e.source).name===source&&ids.get(e.target).name===target&&e.kind===kind),`Missing expected ${source} → ${target} ${kind}`);
}
const index=fs.readFileSync(path.join(site,'class-index.html'),'utf8');
assert.equal((index.match(/https:\/\/github.com\/wighs33\/Pandora-Battle\/blob\//g)||[]).length,data.nodes.length);
for(const name of fs.readdirSync(site).filter(n=>n.endsWith('.html'))){
  const html=fs.readFileSync(path.join(site,name),'utf8');
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(ids.length,new Set(ids).size,`Duplicate HTML id in ${name}`);
  for(const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
    const ref=match[1];if(/^[a-z]+:|^\/\//i.test(ref))continue;
    const [pathname,anchor]=ref.split('#');
    const target=path.resolve(site,pathname.split('?')[0]||name);
    assert(fs.existsSync(target),`Missing link ${name}: ${ref}`);
    if(anchor&&target.endsWith('.html'))assert(fs.readFileSync(target,'utf8').includes(`id="${anchor}"`),`Missing anchor ${name}: ${ref}`);
  }
}
const map=fs.readFileSync(path.join(site,'class-map.html'),'utf8');
for(const [,entry] of map.matchAll(/data-entry="([^"]+)"/g))assert(data.nodes.some(n=>n.name===entry),`Missing entry point ${entry}`);
console.log(JSON.stringify({result:'PASS',types:data.nodes.length,classes:data.meta.classes,structs:data.meta.structs,relationships:data.edges.length,validatedSourceFiles:sourceFiles.size,revision:data.meta.commit},null,2));
