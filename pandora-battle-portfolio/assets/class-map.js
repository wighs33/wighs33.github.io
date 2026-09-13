/* Static C++ source graph. No external runtime, tracking, or generated image. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = window.PANDORA_CLASS_MAP;
  if (!data || !data.nodes.length) {
    $('source-summary').textContent = '데이터를 불러오지 못했습니다. 아래 전체 클래스 링크 목록을 이용해 주세요.';
    return;
  }
  const params = new URLSearchParams(location.search);
  if (params.get('embed') === '1') document.documentElement.classList.add('embedded');
  const NS = 'http://www.w3.org/2000/svg';
  const W = 350, H = 70, STEP = 96;
  const byId = new Map(data.nodes.map(n => [n.id, n]));
  const initial = data.nodes.find(n => n.name === params.get('class')) || data.nodes.find(n => n.name === 'APdPlayerState') || data.nodes[0];
  const state = {selected: initial.id, mode: params.get('view') === 'all' ? 'all' : 'focus', enabled: new Set(['inheritance', 'member', 'signature'])};
  const stage = $('graph-stage'), svg = $('graph'), world = $('graph-world');
  const camera = {x: 0, y: 0, scale: 1};
  let positions = new Map(), visible = [], visibleEdges = [], nodeElements = new Map(), edgeElements = [];
  let bounds = {x:0,y:0,width:1000,height:600};
  let searchTimer, resizeTimer, pointer = null, suppressClickUntil = 0;
  const labelOrigin = {game:'게임', plugin:'외부 플러그인', editor:'에디터'};
  const number = value => value.toLocaleString('ko-KR');
  const groups = [...new Set(data.nodes.map(n => n.group))].sort((a,b) => a.localeCompare(b));
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function se(tag, attrs = {}, text) {
    const node = document.createElementNS(NS, tag);
    for (const [key,value] of Object.entries(attrs)) node.setAttribute(key,String(value));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function link(node, label, className) {
    const a = el('a', label, className);
    a.href = node.url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    return a;
  }
  function fillGroups() {
    const previous = $('group').value;
    $('group').replaceChildren(new Option('전체 영역', 'all'));
    for (const group of groups) {
      const count = data.nodes.filter(n => n.group === group && ($('origin').value === 'all' || n.origin === $('origin').value)).length;
      if (count) $('group').add(new Option(`${group} (${count})`,group));
    }
    if ([...$('group').options].some(o => o.value === previous)) $('group').value = previous;
  }
  const baseNodes = () => data.nodes.filter(n => ($('origin').value === 'all' || n.origin === $('origin').value)
    && ($('group').value === 'all' || n.group === $('group').value) && ($('kind').value === 'all' || n.kind === $('kind').value));
  function matching(nodes) {
    const words = $('search').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    return nodes.filter(n => words.every(word => `${n.qualified} ${n.path}`.toLowerCase().includes(word)));
  }
  function clearFilters() {
    $('search').value = ''; $('origin').value = 'all'; fillGroups(); $('group').value = 'all'; $('kind').value = 'all';
  }
  function choose(id, reset = false) {
    if (!byId.has(id)) return;
    clearTimeout(searchTimer);
    if (reset) {clearFilters();$('direction').value='outgoing';}
    else if (!matching([byId.get(id)]).length) $('search').value='';
    state.selected = id; state.mode = 'focus'; render();
  }
  function renderList(matches) {
    $('list-count').textContent = `${number(matches.length)} / ${number(data.nodes.length)}`;
    const fragment = document.createDocumentFragment();
    const sorted = [...matches].sort((a,b) => a.qualified.localeCompare(b.qualified));
    for (const node of sorted) {
      const row = el('div', undefined, 'class-row' + (node.id === state.selected ? ' selected' : ''));
      const source = link(node, undefined);
      source.title = `${node.qualified} — ${node.path}:${node.line} (새 탭)`;
      source.append(el('strong', node.qualified + ' ↗'), el('small', `${node.group} · ${node.kind}${node.implementation ? ' · CPP' : ''}`));
      const button = el('button', '◎', 'relation-button'); button.type = 'button';
      button.setAttribute('aria-label', `${node.qualified} 관계 보기`);
      button.title = `${node.qualified} 관계 보기`;
      button.addEventListener('click', () => choose(node.id));
      row.append(source,button); fragment.append(row);
    }
    if (!matches.length) fragment.append(el('p','검색 결과가 없습니다. 검색어 또는 필터를 바꿔 주세요.','list-empty'));
    const scroll = $('class-list').scrollTop;
    $('class-list').replaceChildren(fragment); $('class-list').scrollTop = scroll;
  }
  function renderSelection() {
    const node = byId.get(state.selected), detail = $('selection');
    detail.replaceChildren();
    if (!node || !visible.length) { detail.append(el('p','클래스를 찾아 ◎ 버튼으로 관계를 살펴보세요.')); return; }
    detail.append(el('p','SELECTED TYPE','eyebrow'),el('h2',node.qualified));
    detail.append(el('p',`${labelOrigin[node.origin]} · ${node.kind} · ${node.group}`));
    detail.append(el('p',`${node.path}:${node.line}`));
    if (node.bases.length) detail.append(el('p',`부모 타입: ${node.bases.join(', ')}`));
    detail.append(link(node, node.implementation ? 'CPP 선언 열기 ↗' : 'GitHub 헤더 열기 ↗', 'source-link'));
  }
  function positionFocus(nodes, edges) {
    positions = new Map();
    const direction=$('direction').value;
    if (direction!=='both') {
      const others=nodes.filter(n=>n.id!==state.selected);
      const columns=Math.min(stage.clientWidth<550?1:3,Math.max(1,others.length));
      const rows=Math.ceil(others.length/columns),width=columns*(W+32)-32;
      const selectedY=direction==='incoming'?rows*STEP+90:0;
      positions.set(state.selected,{x:(width-W)/2,y:selectedY});
      others.forEach((node,i)=>positions.set(node.id,{x:(i%columns)*(W+32),y:Math.floor(i/columns)*STEP+(direction==='incoming'?0:160)}));
      $('group-layer').replaceChildren(se('text',{x:(width-W)/2,y:selectedY-26,class:'column-label'},'SELECTED / 선택 클래스'));
      return;
    }
    const incoming = new Set(edges.filter(e => e.target === state.selected).map(e => e.source));
    const outgoing = new Set(edges.filter(e => e.source === state.selected).map(e => e.target));
    const left = nodes.filter(n => n.id !== state.selected && incoming.has(n.id) && !outgoing.has(n.id));
    const right = nodes.filter(n => n.id !== state.selected && !left.includes(n));
    const slots = Math.max(1,Math.min(8,Math.max(left.length,right.length)));
    const centerY = ((slots-1)*STEP)/2;
    positions.set(state.selected,{x:0,y:centerY});
    function side(list, direction) {
      const columns = Math.max(1,Math.ceil(list.length/8));
      const rows = Math.ceil(list.length/columns);
      list.forEach((node,i) => positions.set(node.id,{x:direction*(Math.floor(i/rows)+1)*(W+150),y:(i%rows)*STEP + (slots-rows)*STEP/2}));
    }
    side(left,-1); side(right,1);
    const groupLayer = $('group-layer'); groupLayer.replaceChildren();
    if (left.length) groupLayer.append(se('text',{x:-W-150,y:-38,class:'column-label'},'REFERENCED BY / 이 타입을 참조'));
    groupLayer.append(se('text',{x:0,y:centerY-28,class:'column-label'},'SELECTED / 선택 클래스'));
    if (right.length) groupLayer.append(se('text',{x:W+150,y:-38,class:'column-label'},'REFERENCES / 참조하는 타입'));
  }
  function positionAll(nodes) {
    positions = new Map();
    const groupLayer = $('group-layer'); groupLayer.replaceChildren();
    const order = ['Mode','Character','Component','AbilitySystem','Pandora','Definition','UI','GameFeature','AI'];
    const activeGroups = groups.filter(group => nodes.some(n => n.group === group)).sort((a,b) => {
      const ai=order.indexOf(a),bi=order.indexOf(b);
      return (ai<0?99:ai)-(bi<0?99:bi)||a.localeCompare(b);
    });
    const columnCount = activeGroups.length > 8 ? 4 : activeGroups.length > 2 ? 2 : 1;
    const heights = Array(columnCount).fill(0), boxW = W*2+68;
    for (const group of activeGroups) {
      const list = nodes.filter(n => n.group === group);
      const column = heights.indexOf(Math.min(...heights));
      const x = column*(boxW+70),y=heights[column];
      const height = Math.ceil(list.length/2)*STEP+74;
      groupLayer.append(se('rect',{x,y,width:boxW,height,rx:10,class:'group-box'}));
      groupLayer.append(se('text',{x:x+24,y:y+34,class:'group-label'},group));
      groupLayer.append(se('text',{x:x+24,y:y+55,class:'group-subtitle'},`${labelOrigin[list[0].origin]} · ${list.length} TYPES`));
      list.forEach((node,i) => positions.set(node.id,{x:x+24+(i%2)*(W+20),y:y+80+Math.floor(i/2)*STEP}));
      heights[column] += height+70;
    }
  }
  function edgePath(edge, offset) {
    const a = positions.get(edge.source), b = positions.get(edge.target);
    const dx = (b.x+W/2)-(a.x+W/2),dy=(b.y+H/2)-(a.y+H/2);
    if (Math.abs(dx) >= W/2) {
      const startX=dx>0?a.x+W:a.x,endX=dx>0?b.x:b.x+W;
      const startY=a.y+H/2+offset,endY=b.y+H/2+offset;
      const curve=Math.max(40,Math.abs(endX-startX)*.48)*(dx>0?1:-1);
      return `M${startX},${startY} C${startX+curve},${startY} ${endX-curve},${endY} ${endX},${endY}`;
    }
    const startY=dy>0?a.y+H:a.y,endY=dy>0?b.y:b.y+H;
    const startX=a.x+W/2+offset,endX=b.x+W/2+offset,curve=Math.max(30,Math.abs(endY-startY)*.45)*(dy>0?1:-1);
    return `M${startX},${startY} C${startX},${startY+curve} ${endX},${endY-curve} ${endX},${endY}`;
  }
  function highlight(id) {
    const related = new Set([id]);
    for (const edge of visibleEdges) if (edge.source===id||edge.target===id) { related.add(edge.source); related.add(edge.target); }
    for (const [key,node] of nodeElements) node.classList.toggle('is-muted',Boolean(id)&&!related.has(key));
    for (const {node,edge} of edgeElements) {
      const connected=edge.source===id||edge.target===id;
      node.classList.toggle('is-highlighted',Boolean(id)&&connected);
      node.classList.toggle('is-muted',Boolean(id)&&!connected);
    }
  }
  function draw() {
    nodeElements = new Map(); edgeElements=[];
    $('edge-layer').replaceChildren(); $('node-layer').replaceChildren();
    const edgeFragment=document.createDocumentFragment(),nodeFragment=document.createDocumentFragment();
    for (const edge of visibleEdges) {
      const offset={inheritance:-9,member:0,signature:9}[edge.kind];
      const path=se('path',{d:edgePath(edge,offset),class:`edge ${edge.kind}`,'marker-end':`url(#arrow-${edge.kind})`});
      edgeFragment.append(path); edgeElements.push({node:path,edge});
    }
    for (const node of visible) {
      const pos=positions.get(node.id);
      const g=se('g',{class:'node'+(node.id===state.selected?' is-selected':''),transform:`translate(${pos.x},${pos.y})`,'data-kind':node.kind,'data-origin':node.origin,'data-name':node.name});
      const a=se('a',{href:node.url,target:'_blank',rel:'noopener noreferrer','aria-label':`${node.qualified} ${node.implementation?'CPP':'헤더'} 열기 (새 탭)`});
      a.append(se('title',{},`${node.qualified}\n${node.path}:${node.line}\n클릭하여 GitHub 선언 열기`));
      a.append(se('rect',{width:W,height:H,rx:6,class:'node-card'}),se('rect',{x:0,y:12,width:3,height:46,rx:1,class:'node-accent'}));
      const name=se('text',{x:14,y:29,class:'node-name'},node.qualified);
      // Long C++ names retain full spelling; fit within the source-link area.
      if (node.qualified.length>29) { name.setAttribute('textLength','278'); name.setAttribute('lengthAdjust','spacingAndGlyphs'); }
      a.append(name,se('text',{x:14,y:51,class:'node-meta'},`${node.kind.toUpperCase()} · ${node.group}${node.implementation?' · CPP':''}`),se('text',{x:W-25,y:27,class:'node-open'},'↗'));
      g.append(a);
      const focus=se('g',{class:'node-focus',role:'button',tabindex:0,'aria-label':`${node.qualified} 관계 보기`,transform:`translate(${W-38},${H-30})`});
      focus.append(se('title',{},'이 타입의 관계 보기'),se('rect',{width:30,height:24,rx:3}),se('text',{x:15,y:18,'text-anchor':'middle'},'◎'));
      focus.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();choose(node.id);});
      focus.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose(node.id);}});
      g.append(focus);g.addEventListener('pointerenter',()=>highlight(node.id));g.addEventListener('pointerleave',()=>highlight(null));
      g.addEventListener('focusin',()=>highlight(node.id));g.addEventListener('focusout',()=>highlight(null));
      nodeFragment.append(g);nodeElements.set(node.id,g);
    }
    $('edge-layer').append(edgeFragment);$('node-layer').append(nodeFragment);
    if (positions.size) {
      const all=[...positions.values()];
      const minX=Math.min(...all.map(p=>p.x))-40,minY=Math.min(...all.map(p=>p.y))-95;
      bounds={x:minX,y:minY,width:Math.max(...all.map(p=>p.x))+W+40-minX,height:Math.max(...all.map(p=>p.y))+H+65-minY};
    } else bounds={x:0,y:0,width:1000,height:600};
  }
  function render() {
    const eligible=baseNodes(),matches=matching(eligible),set=new Set(eligible.map(n=>n.id));
    if (matches.length&&!matches.some(n=>n.id===state.selected)) {
      const exact=matches.find(n=>n.name.toLowerCase()===$('search').value.trim().toLowerCase());
      state.selected=(exact||matches[0]).id;
    }
    renderList(matches);
    let edges=data.edges.filter(e=>state.enabled.has(e.kind)&&set.has(e.source)&&set.has(e.target));
    if (!matches.length) {visible=[];edges=[];}
    else if (state.mode==='focus') {
      edges=edges.filter(e=>e.source===state.selected||e.target===state.selected);
      if($('direction').value==='outgoing')edges=edges.filter(e=>e.source===state.selected);
      if($('direction').value==='incoming')edges=edges.filter(e=>e.target===state.selected);
      const near=new Set([state.selected,...edges.flatMap(e=>[e.source,e.target])]);
      visible=eligible.filter(n=>near.has(n.id));
    } else {
      visible=matches;const ids=new Set(visible.map(n=>n.id));edges=edges.filter(e=>ids.has(e.source)&&ids.has(e.target));
    }
    visibleEdges=edges;
    if (state.mode==='focus'&&visible.length) positionFocus(visible,visibleEdges);else positionAll(visible);
    draw();frameView();renderSelection();
    $('all-view').setAttribute('aria-pressed',String(state.mode==='all'));
    $('focus-view').setAttribute('aria-pressed',String(state.mode==='focus'));
    $('focus-view').disabled=!matches.length;
    $('direction').disabled=state.mode==='all';
    $('graph-empty').hidden=Boolean(visible.length);
    $('graph-status').textContent=`표시 ${number(visible.length)}개 타입 · ${number(visibleEdges.length)}개 관계`;
    for (const kind of ['inheritance','member','signature']) $('count-'+kind).textContent=number(visibleEdges.filter(e=>e.kind===kind).length);
    const caption=$('stage-caption');caption.replaceChildren();
    if (state.mode==='focus'&&visible.length) {
      const directionLabel={outgoing:'참조하는 타입',incoming:'참조받는 타입',both:'양방향 직접 연결'}[$('direction').value];
      caption.append(el('b',byId.get(state.selected).name),document.createTextNode(' · '+directionLabel));
      if(stage.clientWidth<550&&visible.length>4)caption.append(el('div','드래그로 나머지 연결 탐색 · 화면 맞춤으로 전체 보기'));
      if (!visibleEdges.length) caption.append(el('div','현재 조건에 해당하는 내부 타입 관계가 없습니다.'));
    } else caption.textContent=visible.length?'전체 구조 · 영역별 배치 / 검색 또는 확대하여 탐색':'';
    document.querySelectorAll('[data-entry]').forEach(b=>b.classList.toggle('active',byId.get(state.selected)?.name===b.dataset.entry&&state.mode==='focus'));
  }
  function applyCamera() {
    world.setAttribute('transform',`translate(${camera.x},${camera.y}) scale(${camera.scale})`);
    $('zoom-value').value=`${Math.round(camera.scale*100)}%`;
  }
  function fit() {
    const width=stage.clientWidth,height=stage.clientHeight;
    svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
    camera.scale=Math.min(1.2,(width-30)/bounds.width,(height-30)/bounds.height);
    camera.x=(width-bounds.width*camera.scale)/2-bounds.x*camera.scale;
    camera.y=(height-bounds.height*camera.scale)/2-bounds.y*camera.scale;
    applyCamera();
  }
  function zoom(factor,x=stage.clientWidth/2,y=stage.clientHeight/2) {
    const old=camera.scale;camera.scale=Math.max(.035,Math.min(2.5,old*factor));
    camera.x=x-(x-camera.x)*camera.scale/old;camera.y=y-(y-camera.y)*camera.scale/old;applyCamera();
  }
  function frameView() {
    fit();
    // On a phone start at readable size; explicit Fit still shows every node.
    if(state.mode==='focus'&&visible.length&&stage.clientWidth<550&&camera.scale<.78){
      const selected=positions.get(state.selected);
      camera.scale=Math.min(1,(stage.clientWidth-32)/W);
      camera.x=stage.clientWidth/2-(selected.x+W/2)*camera.scale;
      const selectedScreenY=$('direction').value==='incoming'?stage.clientHeight-130:70;
      camera.y=selectedScreenY-selected.y*camera.scale;applyCamera();
    }
  }
  $('search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{$('class-list').scrollTop=0;render();},140);});
  $('search').addEventListener('keydown',event=>{if(event.key==='Enter'){clearTimeout(searchTimer);state.mode='focus';render();}});
  for (const id of ['origin','group','kind']) $(id).addEventListener('change',()=>{if(id==='origin')fillGroups();$('class-list').scrollTop=0;render();});
  document.querySelectorAll('[data-edge]').forEach(input=>input.addEventListener('change',()=>{if(input.checked)state.enabled.add(input.dataset.edge);else state.enabled.delete(input.dataset.edge);render();}));
  $('all-view').addEventListener('click',()=>{state.mode='all';render();});
  $('focus-view').addEventListener('click',()=>{state.mode='focus';render();});
  $('direction').addEventListener('change',render);
  $('reset').addEventListener('click',()=>{
    clearTimeout(searchTimer);clearFilters();state.selected=initial.id;state.mode='focus';$('direction').value='outgoing';
    document.querySelectorAll('[data-edge]').forEach(input=>{input.checked=true;state.enabled.add(input.dataset.edge);});render();
  });
  document.querySelectorAll('[data-entry]').forEach(button=>{
    const node=data.nodes.find(n=>n.name===button.dataset.entry);
    if(node)button.addEventListener('click',()=>choose(node.id,true));else button.hidden=true;
  });
  $('zoom-in').addEventListener('click',()=>zoom(1.35));$('zoom-out').addEventListener('click',()=>zoom(1/1.35));$('fit').addEventListener('click',fit);
  stage.addEventListener('wheel',event=>{if(event.ctrlKey||event.metaKey){event.preventDefault();const box=stage.getBoundingClientRect();zoom(Math.exp(-event.deltaY*.002),event.clientX-box.left,event.clientY-box.top);}}, {passive:false});
  stage.addEventListener('pointerdown',event=>{
    if(event.button!==0||event.target.closest('.node-focus'))return;
    pointer={id:event.pointerId,x:event.clientX,y:event.clientY,startX:camera.x,startY:camera.y,moved:false};
  });
  stage.addEventListener('pointermove',event=>{
    if(!pointer||pointer.id!==event.pointerId)return;
    const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;
    if(!pointer.moved&&Math.hypot(dx,dy)<6)return;
    if(!pointer.moved){pointer.moved=true;stage.setPointerCapture(event.pointerId);stage.classList.add('dragging');highlight(null);}
    camera.x=pointer.startX+dx;camera.y=pointer.startY+dy;applyCamera();
  });
  function endPointer(event) {
    if(!pointer||pointer.id!==event.pointerId)return;
    if(pointer.moved)suppressClickUntil=performance.now()+250;
    if(stage.hasPointerCapture(event.pointerId))stage.releasePointerCapture(event.pointerId);
    pointer=null;stage.classList.remove('dragging');
  }
  stage.addEventListener('pointerup',endPointer);stage.addEventListener('pointercancel',endPointer);
  stage.addEventListener('pointerleave',event=>{if(pointer&&!pointer.moved)endPointer(event);});
  stage.addEventListener('click',event=>{if(performance.now()<suppressClickUntil){event.preventDefault();event.stopPropagation();}},true);
  stage.addEventListener('keydown',event=>{
    if(event.target!==stage&&event.target!==svg)return;
    const moves={ArrowLeft:[65,0],ArrowRight:[-65,0],ArrowUp:[0,65],ArrowDown:[0,-65]};
    if(moves[event.key]){event.preventDefault();camera.x+=moves[event.key][0];camera.y+=moves[event.key][1];applyCamera();}
    else if(event.key==='+'||event.key==='='){event.preventDefault();zoom(1.35);}
    else if(event.key==='-'){event.preventDefault();zoom(1/1.35);}
    else if(event.key==='0'){event.preventDefault();fit();}
  });
  const summary=$('source-summary');summary.replaceChildren();
  summary.append(el('b',number(data.meta.classes)),document.createTextNode(' 클래스 / '),el('b',number(data.meta.structs)),document.createTextNode(' 구조체'),el('br'),document.createTextNode(`${number(data.meta.headers)}개 헤더 · ${number(data.edges.length)}개 관계 · 플러그인·에디터 포함`));
  $('total-count').textContent=number(data.nodes.length);
  const revision=el('a',`${data.meta.commit.slice(0,7)} ↗`);revision.href=`https://github.com/${data.meta.repository}/tree/${data.meta.commit}`;revision.target='_blank';revision.rel='noopener noreferrer';
  $('revision').append(document.createTextNode(`분석 소스: ${data.meta.repository} · ${data.meta.sourceDate.slice(0,10)} 커밋 `),revision,document.createTextNode(` · ${data.meta.headers}개 헤더 및 ${data.meta.implementations}개 구현 파일 검사.`));
  fillGroups();render();
  let lastWidth=stage.clientWidth;
  new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{
    if(stage.clientWidth!==lastWidth){lastWidth=stage.clientWidth;render();}else frameView();
  },100);}).observe(stage);
  if (params.get('embed')==='1'&&parent!==window) {
    const reportHeight=()=>parent.postMessage({type:'pandora-atlas-height',height:Math.ceil($('atlas').getBoundingClientRect().height)+2},location.origin);
    new ResizeObserver(reportHeight).observe($('atlas')); reportHeight();
  }
})();
