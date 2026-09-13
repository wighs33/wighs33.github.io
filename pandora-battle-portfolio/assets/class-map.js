/* Curated semantic diagrams. Plain DOM, explicit arrows, no external runtime. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = window.PANDORA_CLASS_MAP;
  if (!data?.nodes?.length) { $('source-summary').textContent='관계도 데이터를 읽지 못했습니다. 아래 핵심 클래스 링크 목록을 이용해 주세요.'; return; }
  const params = new URLSearchParams(location.search);
  if (params.get('embed') === '1') document.documentElement.classList.add('embedded');
  const byName = new Map(data.nodes.map(n=>[n.name,n]));
  const byEdge = new Map(data.edges.map(e=>[e.id,e]));
  const categories = new Map(data.categories.map(c=>[c.id,c]));
  const start = byName.get(params.get('class'));
  const state = {selected:start?.name || 'APdPlayerState', category:start?.category || 'pandora', mode:start?'focus':'system', journey:'all', edge:null};
  const pad = n => String(n).padStart(3,'0');
  const cardData = {
    APdPlayerState:['ASC·AttributeSet → 능력과 실제 수치','Pandora·Tree·Inventory → 보유와 성장'],
    UPandoraComponent:['보유 여부·현재 선택·방향별 슬롯','부여한 Ability 핸들 추적'],
    UPandoraDefinition:['이름·무기 조건·단계별 비용·선행 조건','Skill[] → 슬롯별 SkillDefinition'],
    USkillDefinition:['ManaCost · Damage · Time → 비용·피해·시간','AbilitiesToGrant → 실행할 능력 클래스'],
    UPandoraTreeComponent:['GrantedPandoras → 판도라별 현재 Level','PointsAvailable → 남은 성장 포인트'],
    UPandoraSkillSource:['출처 판도라·스킬 에셋·슬롯 인덱스','부여 시 레벨·로드아웃 방향'],
    UPdAbilitySystemComponent:['능력·효과·입력 관리자','SkillSource 복제 목록·발동 대기'],
    UPdGameplayAbility:['비용·이동·연출 관리자와 버프 핸들','Spec.SourceObject → 스킬 출처 조회'],
    UBasicAttributeSet:['체력·마나·스태미나와 최대치','레벨·경험치·공격·방어 속성'],
    UInventoryComponent:['아이템 목록·장착/퀵슬롯 GUID','네트워크 복제 항목'],
    UItemInstance:['공유 ItemDefinition + 개별 ItemId','수량·강화 단계·강화 스탯'],
    UItemDefinition:['기본 스탯·소모 효과·상점 설정','WeaponData → 장착·공격·투사체 규격'],
    UPdSaveGame:['판도라 ID별 레벨·방향별 장착 ID','골드·통계·스킨·매치 기록'],
    UPlayerProfileSubsystem:['플레이어 ID별 SaveGame·스냅샷','저장할 ID·진행 중 ID·재시도'],
    UPandoraDescriptionWidget:['PandoraDefinition + Tree → 설명 구성','DescriptionViewModel → 화면 표시값']
  };
  function el(tag,text,cls) { const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n; }
  function external(url,text,cls) { const a=el('a',text,cls);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a; }
  function button(text,action,cls) {const b=el('button',text,cls);b.type='button';b.addEventListener('click',action);return b;}
  function linkedEdges(name) { return data.edges.filter(e=>e.source===name || e.target===name); }
  function updateURL() { const q=new URLSearchParams(location.search);q.set('class',state.selected);history.replaceState(null,'',`${location.pathname}?${q}${location.hash}`); }
  function select(name,{focus=false,scroll=false,edge=null}={}) {
    if(!byName.has(name))return;
    state.selected=name;state.edge=edge;
    if(focus) {state.mode='focus';state.category=byName.get(name).category;state.journey='all';renderCategories();}
    renderDiagram();renderInspector();updateURL();
    if(scroll){$('inspector').scrollIntoView({block:'nearest'});$('selected-name').focus({preventScroll:true});}
  }
  function renderCategories() {
    $('categories').replaceChildren(...data.categories.map((c,i)=>{
      const b=button('',()=>{
        state.category=c.id;state.mode='system';state.journey='all';state.edge=null;
        state.selected=data.nodes.find(n=>n.category===c.id).name;
        $('search').value='';renderSearch();renderCategories();renderDiagram();renderInspector();updateURL();
      },'category-button');
      b.setAttribute('aria-pressed',String(c.id===state.category));
      b.append(el('b',String(i+1).padStart(2,'0')),el('span',c.title),el('small',`${c.names.length}`));
      return b;
    }));
    const c=categories.get(state.category);
    $('system-number').textContent=`SYSTEM ${String(data.categories.indexOf(c)+1).padStart(2,'0')} / 09 · ${c.names.length} CORE CLASSES`;
    $('system-title').textContent=c.title;$('system-intro').textContent=c.intro;
    $('pandora-guide').hidden=c.id!=='pandora';
  }
  function nodeCard(name) {
    const n=byName.get(name);
    const card=el('article',undefined,'flow-node'+(n.storage==='설정 Data Asset'?' is-config':'')+(name===state.selected?' is-selected':''));
    card.dataset.name=name;
    const a=external(n.url,undefined,'node-source');a.setAttribute('aria-label',`${name} GitHub 헤더 열기 (새 탭)`);
    const top=el('span',undefined,'node-top');top.append(el('span',`#${pad(n.rank)}`,'rank'),el('span',`${n.storage} ↗`));
    a.append(top,el('span',n.role,'node-role'),el('span',name,'node-name'));
    const lines=cardData[name] || n.highlights.slice(0,2).map(h=>h.meaning);
    if(!lines.length)lines.push('추가 저장 필드 없음 · 호출 인자/공통 기능 사용');
    lines.forEach(line=>a.append(el('span',line,'node-data')));
    const detail=button('데이터·관계 보기 ↘',()=>select(name,{scroll:true}),'node-detail');detail.setAttribute('aria-label',`${name} 데이터와 관계 보기`);
    card.append(a,detail);return card;
  }
  function edgeButton(id) {
    const e=byEdge.get(id);
    const b=button('',()=>select(e.source,{scroll:true,edge:id}),`flow-edge ${e.kind}`);
    b.dataset.edge=id;b.title=e.detail;b.setAttribute('aria-label',`${e.source} → ${e.target}: ${e.label}. 관계 설명 보기`);
    b.append(el('span',e.label,'edge-label'),el('span',e.payload,'edge-payload'));
    return b;
  }
  function renderDiagram() {
    const c=categories.get(state.category),focus=state.mode==='focus';
    $('system-view').setAttribute('aria-pressed',String(!focus));$('focus-view').setAttribute('aria-pressed',String(focus));
    $('journey').parentElement.hidden=focus;$('direction-label').hidden=!focus;
    $('journey').replaceChildren(new Option(`모든 흐름 (${c.flows.length})`,'all'),...c.flows.map((f,i)=>new Option(f.title,String(i))));
    $('journey').value=state.journey;
    let flows;
    if(focus) {
      const direction=$('direction').value;
      const edges=linkedEdges(state.selected).filter(e=>direction==='both'||(direction==='outgoing'?e.source===state.selected:e.target===state.selected));
      flows=edges.map((e,i)=>({title:`${String(i+1).padStart(2,'0')} · ${e.label}`,explanation:e.detail,nodes:[e.source,e.target],edges:[e.id]}));
    } else flows=c.flows.filter((_,i)=>state.journey==='all'||String(i)===state.journey);
    const graph=$('diagram'),scroll=graph.scrollTop;
    const lanes=flows.map(f=>{
      const lane=el('section',undefined,'flow-lane');const heading=el('div',undefined,'flow-heading');
      heading.append(el('h3',f.title),el('p',f.explanation));
      const track=el('div',undefined,'flow-track');track.setAttribute('role','group');track.setAttribute('aria-label',f.nodes.join(' → '));
      f.nodes.forEach((name,i)=>{if(i)track.append(edgeButton(f.edges[i-1]));track.append(nodeCard(name));});
      lane.append(heading,track);return lane;
    });
    graph.replaceChildren(...lanes);
    if(!flows.length)graph.append(el('p','이 방향에서 선정한 관계가 없습니다. 양방향 또는 기능별 관계도를 선택해 주세요.','empty'));
    graph.scrollTop=scroll;
    const count=new Set(flows.flatMap(f=>f.nodes)).size;
    $('graph-status').textContent=`${focus?'선택 클래스 연결':'기능별 관계도'} · ${count}개 클래스 (연결된 다른 영역 포함) · ${flows.length}개 흐름`;
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
  function renderSearch() {
    const query=$('search').value.trim().toLocaleLowerCase(),out=$('search-results');out.replaceChildren();out.hidden=!query;
    if(!query){$('search-status').textContent='';return;}
    const words=query.split(/\s+/);
    const matches=data.nodes.filter(n=>{
      const text=[n.name,n.role,n.purpose,n.storage,n.path,...n.highlights.flatMap(h=>[h.meaning,...h.keys])].join(' ').toLocaleLowerCase();
      return words.every(word=>text.includes(word));
    });
    $('search-status').textContent=`핵심 100개 중 ${matches.length}개 검색됨`;
    if(!matches.length)out.append(el('p','검색 결과가 없습니다. 클래스 이름이나 필드 이름, 다른 검색어를 입력해 주세요.','empty'));
    matches.forEach(n=>{
      const b=button('',()=>{select(n.name,{focus:true});$('search').value='';renderSearch();$('diagram').scrollTop=0;},'search-result');
      b.append(el('strong',`#${pad(n.rank)} ${n.name}`),el('small',`${n.role} · ${n.storage}`));out.append(b);
    });
  }
  $('search').addEventListener('input',renderSearch);
  $('journey').addEventListener('change',()=>{state.journey=$('journey').value;renderDiagram();$('diagram').scrollTop=0;});
  $('direction').addEventListener('change',()=>{renderDiagram();$('diagram').scrollTop=0;});
  $('system-view').addEventListener('click',()=>{state.mode='system';renderDiagram();$('diagram').scrollTop=0;});
  function focusConnections(){state.mode='focus';state.edge=null;renderDiagram();$('diagram').scrollTop=0;$('diagram').scrollIntoView({block:'nearest'});}
  $('focus-view').addEventListener('click',focusConnections);$('show-connections').addEventListener('click',focusConnections);
  $('reset').addEventListener('click',()=>{
    Object.assign(state,{category:'pandora',selected:'APdPlayerState',mode:'system',journey:'all',edge:null});
    $('search').value='';$('direction').value='both';renderSearch();renderCategories();renderDiagram();renderInspector();$('diagram').scrollTop=0;updateURL();
  });
  $('class-list').replaceChildren(...data.nodes.map(n=>{
    const b=button('',()=>{select(n.name,{focus:true});$('diagram').scrollTop=0;$('diagram').scrollIntoView({block:'nearest'});});b.dataset.name=n.name;b.setAttribute('aria-pressed','false');
    b.append(el('strong',`#${pad(n.rank)} ${n.name}`),el('small',`${n.role} · ${categories.get(n.category).title}`));return b;
  }));
  $('index-count').textContent='100 / 100';
  $('source-summary').textContent=`100개 클래스 · ${data.edges.length}개 설명된 관계 · 9개 기능 영역`;
  $('revision').append(el('span',`소스 기준: ${data.meta.sourceDate.slice(0,10)} · `),external(`https://github.com/wighs33/Pandora-Battle/tree/${data.meta.commit}`,data.meta.commit.slice(0,12)+' ↗'));
  renderCategories();renderDiagram();renderInspector();
  let reportedHeight=0,frame;
  function reportHeight(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{const height=Math.ceil($('atlas').getBoundingClientRect().height)+2;if(height!==reportedHeight){reportedHeight=height;if(parent!==window)parent.postMessage({type:'pandora-atlas-height',height},location.origin);}});}
  new ResizeObserver(reportHeight).observe($('atlas'));addEventListener('resize',reportHeight);reportHeight();
})();
