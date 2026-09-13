/* Canonical UML class navigation, source links and an independent detail panel. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id),data=window.PANDORA_CLASS_MAP,model=window.PANDORA_UML;
  if(!data?.nodes?.length||!model){$('source-summary').textContent='데이터를 읽지 못했습니다. 아래 클래스 링크 목록을 이용해 주세요.';return;}
  const params=new URLSearchParams(location.search),embedded=params.get('embed')==='1';
  if(embedded)document.documentElement.classList.add('embedded');
  const byName=new Map(data.nodes.map(n=>[n.name,n])),categories=new Map(data.categories.map(c=>[c.id,c]));
  const first=byName.get(params.get('class'))||byName.get('APdPlayerState');
  const state={root:first.name,selected:first.name,category:first.category,edge:null,expanded:false,trail:[]};
  const cache=new Map(),camera={x:0,y:0,scale:1},pad=n=>String(n).padStart(3,'0');
  let view,drag=null;
  function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
  function external(url,text,cls){const a=el('a',text,cls);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
  function button(text,action,cls){const b=el('button',text,cls);b.type='button';b.addEventListener('click',action);return b;}
  function linkedEdges(name){return data.edges.filter(e=>e.source===name||e.target===name);}
  function sourceURL(name){return 'class-map.html?v=uml-1&class='+encodeURIComponent(name);}
  function updateURL(push){const q=new URLSearchParams(location.search);q.set('class',state.root);q.set('v','uml-1');history[push?'pushState':'replaceState'](null,'',`${location.pathname}?${q}`);}
  function openGraph(name,{push=true}={}){
    if(!byName.has(name))return;
    const changed=name!==state.root;
    if(push&&changed)state.trail.push(state.root);
    state.root=name;state.selected=name;state.edge=null;state.expanded=false;state.category=byName.get(name).category;
    $('search').value='';renderSearch();renderCategories();renderDiagram();renderInspector();updateURL(push&&changed);
  }
  function select(name,{scroll=false,edge=null}={}){showDetails(name,edge,scroll);}
  function showDetails(name=state.root,edge=null,scroll=true){
    state.selected=name;state.edge=edge;renderInspector();$('detail-disclosure').open=true;
    if($('diagram-panel').classList.contains('is-expanded'))toggleExpand();
    if(scroll)requestAnimationFrame(()=>{$('detail-disclosure').scrollIntoView({block:'start',behavior:'smooth'});$('selected-name').focus({preventScroll:true});});
  }
  function renderCategories(){
    $('categories').replaceChildren(...data.categories.map((c,i)=>{
      const b=button('',()=>openGraph(c.names[0]),'category-button');
      b.setAttribute('aria-pressed',String(c.id===state.category));
      b.append(el('b',String(i+1).padStart(2,'0')),el('span',c.title),el('small',String(c.names.length)));return b;
    }));
    const c=categories.get(state.category);
    $('class-picker').replaceChildren(...[...c.names].sort((a,b)=>byName.get(a).rank-byName.get(b).rank).map(name=>{const n=byName.get(name);return new Option(`#${pad(n.rank)} ${name} · ${n.role}`,name);}));
    $('class-picker').value=state.root;
  }
  function svg(tag,attrs={}){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);return n;}
  function highlight(names=[],ids=[]){
    const active=new Set(names),edges=new Set(ids);$('graph-world').classList.toggle('is-highlighting',!!(names.length||ids.length));
    document.querySelectorAll('.uml-node').forEach(n=>n.classList.toggle('is-active',active.has(n.dataset.name)));
    document.querySelectorAll('.wire-group').forEach(n=>n.classList.toggle('is-active',edges.has(n.dataset.edge)));
    document.querySelectorAll('.uml-row').forEach(n=>n.classList.remove('is-active'));
    view.edges.filter(e=>edges.has(e.id)&&e.sourceRow>=0).forEach(e=>{
      const card=[...document.querySelectorAll('.uml-node')].find(n=>n.dataset.name===e.source);
      card?.querySelectorAll('.uml-row')[e.sourceRow]?.classList.add('is-active');
    });
    if(!names.length&&!ids.length)$('edge-tooltip').hidden=true;
  }
  function highlightNode(name){const links=view.edges.filter(e=>e.source===name||e.target===name);highlight([name,...links.flatMap(e=>[e.source,e.target])],links.map(e=>e.id));}
  function tooltip(e,event){
    const tip=$('edge-tooltip');tip.textContent=e.label+'\n'+e.payload;tip.hidden=false;
    const r=$('diagram').getBoundingClientRect();
    tip.style.left=Math.max(8,Math.min((event?.clientX??r.left+24)-r.left+16,r.width-tip.offsetWidth-12))+'px';
    tip.style.top=Math.max(8,Math.min((event?.clientY??r.top+24)-r.top+16,r.height-tip.offsetHeight-12))+'px';
  }
  function card(n){
    const a=el('article',undefined,'uml-node'+(n.name===state.root?' is-root':'')+(/Definition$/.test(n.name)?' is-config':''));
    a.dataset.name=n.name;a.style.cssText=`left:${n.x}px;top:${n.y}px;width:${n.width}px;height:${n.height}px`;
    const open=button('',()=>openGraph(n.name),'uml-open');open.setAttribute('aria-label',`${n.name} 구조도 열기`);
    const header=el('span',undefined,'uml-header'),role=el('span',undefined,'uml-role');
    role.append(el('span',n.role),el('span',n.name===state.root?'중심 클래스':/Definition$/.test(n.name)?'공유 설정':'#'+pad(n.rank)));
    const name=el('span',n.name,'uml-name');if(n.name.length>32)name.style.fontSize='11px';
    header.append(role,name);open.append(header);
    const fields=el('span',undefined,'uml-fields');
    for(const row of n.rows){
      const line=el('span',undefined,'uml-row'+(row.nested?' nested':''));line.dataset.keys=row.keys.join(',');
      line.title=row.fields.map(f=>f.declaration).join('\n')+'\n'+row.meaning;
      line.append(el('code',row.label));
      // Keep field names fully available; long object types are conveyed by the connected block.
      if(row.type&&row.type.length<=14&&row.label.length<25)line.append(el('small',row.type));
      fields.append(line);
    }
    if(!n.rows.length)fields.append(el('span','추가 필드 없음 · 호출 / 부모 상태 사용','uml-empty'));
    open.append(fields);
    const footer=el('div',undefined,'uml-footer');
    const detail=button('내용 ↓',()=>showDetails(n.name));detail.setAttribute('aria-label',`${n.name} 세부 설명 보기`);
    const link=external(n.url,'GitHub ↗');link.setAttribute('aria-label',`${n.name} GitHub 헤더 열기 (새 탭)`);
    footer.append(detail,el('span','블록 클릭 → 구조도','open-label'),link);a.append(open,footer);
    a.addEventListener('pointerenter',()=>highlightNode(n.name));a.addEventListener('pointerleave',()=>highlight());
    a.addEventListener('focusin',()=>highlightNode(n.name));a.addEventListener('focusout',()=>highlight());return a;
  }
  function renderDiagram(){
    const landscape=$('diagram').clientWidth/$('diagram').clientHeight>1.55;
    const key=state.root+':'+state.expanded+':'+landscape;
    if(!cache.has(key))cache.set(key,model.routeView(model.buildView(data,state.root,state.expanded,landscape)));
    view=cache.get(key);
    view.landscape=landscape;
    const world=$('graph-world');world.replaceChildren();world.classList.remove('is-highlighting');$('edge-tooltip').hidden=true;
    const wires=svg('svg',{class:'graph-wires',width:1,height:1,'aria-label':'클래스 사이의 관계'}),defs=svg('defs');
    for(const [id,color]of [['ownership','#8dbfdb'],['reference','#c1a3ef'],['config','#c1a3ef'],['runtime','#acb8a5'],['projection','#acb8a5'],['sequence','#acb8a5'],['inheritance','#8dbfdb']]){
      const marker=svg('marker',{id:'arrow-'+id,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:7,markerHeight:7,orient:'auto-start-reverse',markerUnits:'userSpaceOnUse'});
      marker.append(svg('path',{d:'M0,1 L9,5 L0,9 Z',fill:color}));defs.append(marker);
    }
    wires.append(defs);
    for(const e of view.edges){
      const group=svg('g',{class:'wire-group','data-edge':e.id}),d=model.roundedPath(e.points);
      group.append(svg('path',{d,class:'wire-halo'}),svg('path',{d,class:'wire '+e.kind,'marker-end':'url(#arrow-'+e.kind+')'}));
      const hit=svg('path',{d,class:'wire-hit',tabindex:0,role:'button','aria-label':`${e.source} → ${e.target}: ${e.label}. 세부 설명 보기`});
      hit.addEventListener('pointerenter',ev=>{highlight([e.source,e.target],[e.id]);tooltip(e,ev);});
      hit.addEventListener('pointermove',ev=>tooltip(e,ev));hit.addEventListener('pointerleave',()=>highlight());
      hit.addEventListener('focus',()=>{highlight([e.source,e.target],[e.id]);tooltip(e);});hit.addEventListener('blur',()=>highlight());
      const detail=()=>showDetails(e.source,e.id);
      hit.addEventListener('click',detail);hit.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();detail();}});
      group.append(hit);wires.append(group);
    }
    world.append(wires,...view.nodes.map(card));
    $('graph-title').textContent=state.root;$('graph-role').textContent=byName.get(state.root).role+' · '+byName.get(state.root).storage;
    $('graph-status').textContent=`${view.nodes.length}개 블록 · ${view.edges.length}개 연결 · `+($('diagram').clientWidth<520?'드래그 이동 · 전체 맞춤으로 구조 보기':'드래그 이동 / Ctrl + 휠 확대');
    $('more-connections').hidden=!view.hiddenConnections&&!state.expanded;
    $('more-connections').textContent=state.expanded?'기본 구조로':`추가 연결 ${view.hiddenConnections}개`;
    $('standalone').href=sourceURL(state.root);$('back').disabled=!state.trail.length;
    fit();
  }
  function applyCamera(){
    $('graph-world').style.transform=`translate(${camera.x}px,${camera.y}px) scale(${camera.scale})`;
    $('zoom-level').textContent=Math.round(camera.scale*100)+'%';
  }
  function fit(overview=false){
    if(!view)return;const b=view.bounds,d=$('diagram');
    camera.scale=Math.min((d.clientWidth-28)/b.width,(d.clientHeight-28)/b.height,1.35);
    camera.x=(d.clientWidth-b.width*camera.scale)/2-b.x*camera.scale;camera.y=(d.clientHeight-b.height*camera.scale)/2-b.y*camera.scale;
    // On a phone, start with readable data. The explicit fit action gives the overview.
    if(d.clientWidth<520&&!overview){const root=view.nodes.find(n=>n.name===state.root);camera.scale=.85;camera.x=(d.clientWidth-root.width*camera.scale)/2-root.x*camera.scale;camera.y=32-root.y*camera.scale;}
    else if(d.clientWidth<520)camera.y=24-b.y*camera.scale;
    applyCamera();
  }
  function zoom(factor,x=$('diagram').clientWidth/2,y=$('diagram').clientHeight/2){const next=Math.max(.2,Math.min(2.4,camera.scale*factor)),ratio=next/camera.scale;camera.x=x-(x-camera.x)*ratio;camera.y=y-(y-camera.y)*ratio;camera.scale=next;applyCamera();}
  function toggleExpand(){
    if(embedded){window.open(sourceURL(state.root)+'&wide=1','_blank','noopener');return;}
    const expanded=$('diagram-panel').classList.toggle('is-expanded');document.body.classList.toggle('has-expanded',expanded);
    $('expand').setAttribute('aria-pressed',String(expanded));$('expand').textContent=expanded?'돌아가기 ↙':'넓게 보기 ⛶';renderDiagram();
  }
  function renderSearch(){
    const query=$('search').value.trim().toLocaleLowerCase(),out=$('search-results');out.replaceChildren();out.hidden=!query;
    if(!query){$('search-status').textContent='';return;}
    const words=query.split(/\s+/),matches=data.nodes.filter(n=>{const text=[n.name,n.role,n.purpose,...n.highlights.flatMap(h=>[h.meaning,...h.keys])].join(' ').toLocaleLowerCase();return words.every(w=>text.includes(w));});
    $('search-status').textContent=`핵심 100개 중 ${matches.length}개 검색됨`;
    if(!matches.length)out.append(el('p','검색 결과가 없습니다.','empty'));
    matches.forEach(n=>{const b=button('',()=>openGraph(n.name),'search-result');b.append(el('strong',`#${pad(n.rank)} ${n.name}`),el('small',n.role));out.append(b);});
  }
  function declaration(field) {
    const wrapper=el('div',undefined,'declaration');
    const source=external(field.url);source.append(el('code',field.declaration+' ↗'));wrapper.append(source);
    for(const s of field.schemas) {
      const d=el('details',undefined,'nested-schema');d.append(el('summary',`${s.name} · 내부 데이터 ${s.fields.length}개`));
      d.append(external(s.url,'구조체 선언 ↗'));
      s.fields.forEach(f=>d.append(declaration(f)));wrapper.append(d);
    }
    return wrapper;
  }
  function referenceNames(fields) {
    const found=new Set();
    function visit(f){f.references.forEach(n=>found.add(n));f.schemas.forEach(s=>s.fields.forEach(visit));}
    fields.forEach(visit);return [...found];
  }
  function renderInspector() {
    const n=byName.get(state.selected);
    $('detail-label').textContent=n.name;
    $('selected-meta').textContent=`#${pad(n.rank)} · ${n.role} · ${n.storage}`;
    $('selected-name').textContent=n.name;$('selected-purpose').textContent=n.purpose;
    $('selected-source').href=n.url;
    const target=$('field-details');target.replaceChildren();target.scrollTop=0;
    target.append(el('p','아래는 헤더의 실제 필드입니다. 선언에 나온 숫자는 C++ 기본값이며, Data Asset에 설정된 실제 콘텐츠 값과 다를 수 있습니다.','data-note'));
    for(const h of n.highlights) {
      const group=el('div',undefined,'field-group');group.append(el('p',h.meaning));
      const keys=el('div',undefined,'field-keys');h.fields.forEach(f=>keys.append(external(f.url,f.key+' ↗')));group.append(keys);
      const raw=el('details');raw.append(el('summary','실제 선언과 하위 데이터 펼치기'));h.fields.forEach(f=>raw.append(declaration(f)));group.append(raw);
      const refs=referenceNames(h.fields).filter(name=>name!==n.name);
      refs.forEach(name=>{
        const ref=byName.get(name),preview=el('div',undefined,'reference-preview');
        preview.append(el('b',`${name} · ${ref.role}`),el('p',ref.purpose),button(`${ref.role} 데이터 보기 →`,()=>select(name,{scroll:false})));
        group.append(preview);
      });
      target.append(group);
    }
    if(!n.fields.length)target.append(el('p','이 클래스가 추가로 선언한 저장 필드는 없습니다. 부모의 상태 또는 호출 시 전달된 인자를 사용합니다.','data-note'));
    const all=el('details',undefined,'field-group');all.append(el('summary',`이 클래스의 직접 선언 필드 전체 (${n.fields.length})`));n.fields.forEach(f=>all.append(declaration(f)));target.append(all);
    const relations=$('relation-details');relations.replaceChildren();relations.scrollTop=0;
    const linked=linkedEdges(n.name).sort((a,b)=>(b.id===state.edge)-(a.id===state.edge));
    linked.forEach(e=>{
      const other=byName.get(e.source===n.name?e.target:e.source),card=el('article',undefined,'relation-card'+(e.id===state.edge?' is-active':''));
      card.dataset.edge=e.id;
      card.append(el('span',`${e.source===n.name?'이 클래스 → 대상':'다른 클래스 → 이 클래스'} · ${e.label}`,'relationship-kind'));
      card.append(el('div',`${e.source} → ${e.target}`,'relationship-names'),el('p',e.payload,'relation-payload'),el('p',e.detail));
      const actions=el('div',undefined,'relation-actions');actions.append(button(`${other.role} 데이터 →`,()=>select(other.name,{scroll:false})),external(e.evidence.url,`근거 소스 L${e.evidence.line} ↗`));card.append(actions);relations.append(card);
    });
    if(!linked.length)relations.append(el('p','선정 범위에서 확인한 직접 관계가 없습니다. 클래스 헤더의 실제 선언을 확인해 주세요.','data-note'));
    document.querySelectorAll('.class-list button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.name===n.name)));
  }

  $('search').addEventListener('input',renderSearch);
  $('search').addEventListener('keydown',e=>{if(e.key==='Escape'){$('search').value='';renderSearch();}});
  $('class-picker').addEventListener('change',()=>openGraph($('class-picker').value));
  $('back').addEventListener('click',()=>{if(state.trail.length)history.back();});
  $('zoom-in').addEventListener('click',()=>zoom(1.2));$('zoom-out').addEventListener('click',()=>zoom(1/1.2));$('fit').addEventListener('click',()=>fit(true));
  $('expand').addEventListener('click',toggleExpand);$('open-details').addEventListener('click',()=>showDetails());
  $('more-connections').addEventListener('click',()=>{state.expanded=!state.expanded;renderDiagram();});
  $('diagram').addEventListener('pointerdown',e=>{
    if(e.button!==0||e.target.closest('.uml-node,.wire-hit'))return;
    drag={id:e.pointerId,x:e.clientX,y:e.clientY,cx:camera.x,cy:camera.y};$('diagram').setPointerCapture(e.pointerId);$('diagram').classList.add('dragging');
  });
  $('diagram').addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;camera.x=drag.cx+e.clientX-drag.x;camera.y=drag.cy+e.clientY-drag.y;applyCamera();});
  function endDrag(){drag=null;$('diagram').classList.remove('dragging');}
  $('diagram').addEventListener('pointerup',endDrag);$('diagram').addEventListener('pointercancel',endDrag);$('diagram').addEventListener('lostpointercapture',endDrag);
  $('diagram').addEventListener('wheel',e=>{if(!e.ctrlKey&&!e.metaKey)return;e.preventDefault();const r=$('diagram').getBoundingClientRect();zoom(Math.exp(-e.deltaY*.003),e.clientX-r.left,e.clientY-r.top);},{passive:false});
  $('diagram').addEventListener('keydown',e=>{
    if(e.target!==$('diagram'))return;
    if(e.key==='+'||e.key==='=')zoom(1.2);else if(e.key==='-')zoom(1/1.2);else if(e.key==='0')fit(true);
    else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){camera.x+=e.key==='ArrowLeft'?40:e.key==='ArrowRight'?-40:0;camera.y+=e.key==='ArrowUp'?40:e.key==='ArrowDown'?-40:0;applyCamera();}else return;e.preventDefault();
  });
  addEventListener('keydown',e=>{if(e.key==='Escape'&&$('diagram-panel').classList.contains('is-expanded'))toggleExpand();});
  addEventListener('popstate',()=>{const name=new URLSearchParams(location.search).get('class');if(byName.has(name)){if(state.trail.at(-1)===name)state.trail.pop();openGraph(name,{push:false});}});
  $('class-list').replaceChildren(...data.nodes.map(n=>{const b=button('',()=>{openGraph(n.name);$('diagram-panel').scrollIntoView({block:'start'});});b.dataset.name=n.name;b.append(el('strong',`#${pad(n.rank)} ${n.name}`),el('small',n.role));return b;}));
  $('source-summary').textContent='100개 핵심 클래스 · 9개 기능 영역';
  $('revision').append(el('span',`소스 기준 ${data.meta.sourceDate.slice(0,10)} · `),external(`https://github.com/wighs33/Pandora-Battle/tree/${data.meta.commit}`,data.meta.commit.slice(0,12)+' ↗'));
  renderCategories();renderDiagram();renderInspector();updateURL(false);
  if(params.get('wide')==='1'&&!embedded)toggleExpand();
  let lastSize='';new ResizeObserver(()=>{const d=$('diagram'),size=d.clientWidth+':'+d.clientHeight;if(size!==lastSize){lastSize=size;if((d.clientWidth/d.clientHeight>1.55)!==view.landscape)renderDiagram();else fit();}}).observe($('diagram'));
  let reportedHeight=0,frame;
  function reportHeight(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{const height=Math.ceil($('atlas').getBoundingClientRect().height)+2;if(height!==reportedHeight){reportedHeight=height;if(parent!==window)parent.postMessage({type:'pandora-atlas-height',height},location.origin);}});}
  new ResizeObserver(reportHeight).observe($('atlas'));addEventListener('resize',reportHeight);reportHeight();
})();
