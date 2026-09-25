import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../pandora-battle-portfolio/assets/',import.meta.url);
const read=file=>fs.readFileSync(new URL(file,root),'utf8');
const sandbox={window:{}};
vm.runInNewContext(read('class-tree-model.js'),sandbox);
const model=sandbox.window.PANDORA_TREE;
const raw=read('class-map-data.js');
const data=JSON.parse(raw.slice(raw.indexOf(' = ')+3).trim().slice(0,-1));
const names=new Set(data.nodes.map(n=>n.name));
const nodes=new Map(data.nodes.map(n=>[n.name,n]));
let checked=0;
function verify(items,expected){
  const found=[];
  function walk(item,parent=null,folder=null){
    if(item.kind==='type'){
      assert(names.has(item.name));found.push(item.name);
      if(parent?.kind==='type')assert(nodes.get(item.name).bases.includes(parent.name));
      if(parent?.kind==='external')assert(nodes.get(item.name).bases.includes(parent.label));
      if(folder!==null)assert.equal(nodes.get(item.name).folder,folder);
    }
    for(const child of item.children||[])walk(child,item,item.kind==='folder'?item.path:folder);
  }
  items.forEach(item=>walk(item));
  assert.equal(found.length,new Set(found).size,'Duplicate tree item');
  assert.deepEqual([...found].sort(),[...expected].sort());checked+=found.length;
}
for(const kind of ['all','class','struct','namespace','enum']){
  const filtered=data.nodes.filter(n=>model.matches(n,'',kind));
  verify(model.folders(filtered),filtered.map(n=>n.name));
  verify(model.inheritance(filtered),filtered.filter(n=>['class','struct'].includes(n.kind)).map(n=>n.name));
}
assert(model.matches(nodes.get('UPandoraComponent'),'OwnedSkillSources','class'));
assert(model.matches(nodes.get('FPandoraSkillBinder'),'GrantPandoraContent','all'));
assert(!model.matches(nodes.get('USkillAbility'),'unmatched-query-xyz','all'));
console.log(JSON.stringify({result:'PASS',declarations:names.size,treePlacements:checked,views:['folder','inheritance'],filters:5}));
