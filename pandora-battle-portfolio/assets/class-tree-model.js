/* Source folders and inheritance are separate hierarchies, never inferred from filenames. */
(() => {
  'use strict';
  const sort = (a,b) => a.label.localeCompare(b.label,'en');
  function inheritance(nodes,{local=false}={}) {
    const classes=nodes.filter(n=>n.kind==='class'||n.kind==='struct');
    const byName=new Map(classes.map(n=>[n.name,{kind:'type',name:n.name,label:n.name,children:[]}]));
    const roots=[],external=new Map(),source=new Map(nodes.map(n=>[n.name,n]));
    for(const n of classes){
      const item=byName.get(n.name),base=n.bases[0];
      if(base&&byName.has(base)&&(!local||source.get(base).folder===n.folder))byName.get(base).children.push(item);
      else if(base&&!local){
        if(!external.has(base)){const group={kind:'external',label:base,children:[]};external.set(base,group);roots.push(group);}
        external.get(base).children.push(item);
      }else roots.push(item);
    }
    for(const item of byName.values())item.children.sort(sort);
    return roots.sort(sort);
  }
  function folders(nodes){
    const root={kind:'folder',label:'Source / LabProject',path:'',children:[],nodes:[]};
    for(const n of nodes){
      let folder=root;
      for(const part of n.folder.split('/').filter(Boolean)){
        let next=folder.children.find(c=>c.kind==='folder'&&c.label===part);
        if(!next){next={kind:'folder',label:part,path:[folder.path,part].filter(Boolean).join('/'),children:[],nodes:[]};folder.children.push(next);}
        folder=next;
      }
      folder.nodes.push(n);
    }
    function finish(folder){
      folder.children.sort(sort).forEach(finish);
      const classes=folder.nodes.filter(n=>n.kind==='class');
      const other=folder.nodes.filter(n=>n.kind!=='class');
      folder.children.push(...inheritance(classes,{local:true}));
      if(other.length)folder.children.push({kind:'data',label:'데이터·도우미',children:other.sort((a,b)=>a.name.localeCompare(b.name)).map(n=>({kind:'type',name:n.name,label:n.name,children:[]}))});
      folder.count=folder.nodes.length+folder.children.filter(c=>c.kind==='folder').reduce((sum,c)=>sum+c.count,0);
      delete folder.nodes;
    }
    finish(root);return root.children;
  }
  function matches(n,query,kind){
    if(kind!=='all'&&n.kind!==kind)return false;
    const text=[n.name,n.qualified,n.role,n.folder,...n.fields.map(f=>f.key),...n.methods.map(m=>m.name)].join(' ').toLowerCase();
    return query.trim().toLowerCase().split(/\s+/).every(word=>text.includes(word));
  }
  const model={folders,inheritance,matches};
  if(typeof module!=='undefined')module.exports=model;
  else window.PANDORA_TREE=model;
})();
