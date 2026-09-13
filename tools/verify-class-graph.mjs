import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const assets=new URL('../pandora-battle-portfolio/assets/',import.meta.url),context={window:{}};
vm.createContext(context);
for(const file of ['class-map-data.js','class-graph-model.js'])vm.runInContext(fs.readFileSync(new URL(file,assets),'utf8'),context);
const {PANDORA_CLASS_MAP:data,PANDORA_UML:model}=context.window;
const evidence=new Map(data.edges.map(e=>[e.id,e]));
function onBoundary(p,n){return (p.x===n.x||p.x===n.x+n.width)&&p.y>=n.y&&p.y<=n.y+n.height||(p.y===n.y||p.y===n.y+n.height)&&p.x>=n.x&&p.x<=n.x+n.width;}
function intersects(a,b,n){return a.x===b.x?a.x>n.x&&a.x<n.x+n.width&&Math.max(a.y,b.y)>n.y&&Math.min(a.y,b.y)<n.y+n.height:a.y>n.y&&a.y<n.y+n.height&&Math.max(a.x,b.x)>n.x&&Math.min(a.x,b.x)<n.x+n.width;}
let graphs=0,routes=0,fields=0;
for(const node of data.nodes){
  for(const row of model.makeRows(node)){assert(row.fields.every(f=>row.keys.includes(f.key)));fields+=row.fields.length;}
  for(const expanded of [false,true])for(const landscape of [false,true]){
    const graph=model.routeView(model.buildView(data,node.name,expanded,landscape));graphs++;
    const byName=new Map(graph.nodes.map(n=>[n.name,n]));
    assert.equal(byName.size,graph.nodes.length,'Every class appears once in a view');assert(byName.has(node.name));
    const reached=new Set([node.name]);
    for(let i=0;i<graph.nodes.length;i++)for(const e of graph.edges)if(reached.has(e.source)||reached.has(e.target)){reached.add(e.source);reached.add(e.target);}
    assert.equal(reached.size,graph.nodes.length,`Disconnected blocks in ${node.name}`);
    for(const edge of graph.edges){
      routes++;assert(evidence.has(edge.id));assert.equal(edge.evidence.url,evidence.get(edge.id).evidence.url);
      assert(onBoundary(edge.points[0],byName.get(edge.source)),`Source port detached: ${node.name}: ${edge.id}`);
      assert(onBoundary(edge.points.at(-1),byName.get(edge.target)),`Target port detached: ${node.name}: ${edge.id}`);
      assert(!/NaN|Infinity/.test(model.roundedPath(edge.points)));
      edge.points.forEach((p,i)=>{
        if(!i)return;const a=edge.points[i-1];assert(a.x===p.x||a.y===p.y,'Routes remain orthogonal');
        for(const box of graph.nodes)assert(!intersects(a,p,box),`Wire crosses a block: ${node.name}: ${edge.id}: ${box.name}`);
      });
    }
  }
}
const player=model.buildView(data,'APdPlayerState'),names=player.nodes.map(n=>n.name);
for(const edge of ['APdPlayerState>UPdAbilitySystemComponent','UPdAbilitySystemComponent>UPandoraSkillSource','UPandoraSkillSource>UPandoraDefinition'])assert(player.edges.some(e=>e.id===edge));
assert.equal(names.filter(n=>n==='UPandoraDefinition').length,1);
const definition=player.nodes.find(n=>n.name==='UPandoraDefinition');
assert(definition.rows.some(r=>r.nested&&r.keys.includes('SkillDefinition')));
assert(definition.rows.some(r=>r.nested&&r.keys.includes('RequiredLevel')));
const modelFile=fileURLToPath(new URL('class-graph-model.js',assets));
console.log(JSON.stringify({result:'PASS',canonicalClasses:data.nodes.length,layoutVariants:graphs,routedConnections:routes,umlFieldChecks:fields,model:modelFile},null,2));
