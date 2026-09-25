/* Complete source tree; selecting a declaration opens independent details below. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id),data=window.PANDORA_CLASS_MAP,model=window.PANDORA_TREE;
  if(!data?.nodes?.length||!model){$('tree-status').textContent='데이터를 불러오지 못했습니다. 전체 선언 링크 목록을 이용해 주세요.';return;}
  const params=new URLSearchParams(location.search),embedded=params.get('embed')==='1',version=data.meta.version;
  if(embedded)document.documentElement.classList.add('embedded');
  const byName=new Map(data.nodes.map(n=>[n.name,n]));
  const labels={class:'클래스',struct:'구조체',namespace:'네임스페이스',enum:'열거형'};
  const state={view:params.get('view')==='inheritance'?'inheritance':'folder',selected:null};
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const button=(text,action,cls)=>{const b=el('button',text,cls);b.type='button';b.addEventListener('click',action);return b;};
  const external=(url,text)=>{const a=el('a',text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;};
  function sourceURL(name){const q=new URLSearchParams({v:version});if(name)q.set('class',name);return 'class-map.html?'+q;}
  function updateURL(push=false){const q=new URLSearchParams(location.search);q.set('v',version);q.set('view',state.view);if(state.selected)q.set('class',state.selected);else q.delete('class');history[push?'pushState':'replaceState'](null,'',location.pathname+'?'+q);$('standalone').href=sourceURL(state.selected);}
  function nameButton(n){const b=button(n.name,()=>select(n.name),'type-name');b.dataset.name=n.name;b.setAttribute('aria-label',n.name+' 세부 설명 보기');b.setAttribute('aria-pressed',String(n.name===state.selected));return b;}
  function typeRow(n,{path=false}={}){
    const row=el('div',undefined,'type-row');row.append(el('span',{class:'C',struct:'S',namespace:'N',enum:'E'}[n.kind],'type-icon '+n.kind),nameButton(n));
    const note=n.bases.length?'상속 '+n.bases.join(' · '):n.role!==n.name?n.role:labels[n.kind];
    row.append(el('span',path?n.folder||'LabProject':note,'type-note'));row.title=n.qualified+' · '+n.path;return row;
  }
  function treeItem(item,depth=0){
    const li=el('li',undefined,'tree-item '+item.kind),children=item.children||[];
    if(item.kind==='type'){
      if(children.length){const d=el('details',undefined,'tree-branch inheritance-branch');d.open=true;const s=el('summary');s.append(typeRow(byName.get(item.name)));d.append(s,treeList(children,depth+1));li.append(d);}
      else li.append(typeRow(byName.get(item.name)));
    }else{
      const d=el('details',undefined,'tree-branch');d.open=item.kind!=='data'&&depth<2;
      const s=el('summary'),row=el('span',undefined,'folder-row'),projectBase=item.kind==='external'&&byName.get(item.label);
      row.append(el('span',item.kind==='external'?'↳':item.kind==='data'?'{}':'▱','folder-icon'),projectBase?nameButton(projectBase):el('span',item.label),el('small',projectBase?'필터 밖 부모':item.kind==='external'?'외부 타입':String(item.count??children.length)));
      s.append(row);d.append(s,treeList(children,depth+1));li.append(d);
    }
    return li;
  }
  function treeList(items,depth=0){const ul=el('ul',undefined,'tree-list');items.forEach(item=>ul.append(treeItem(item,depth)));return ul;}
  function renderTree(){
    const query=$('search').value,kind=$('kind-filter').value;
    const filtered=data.nodes.filter(n=>model.matches(n,query,kind));
    $('class-tree').replaceChildren();
    if(query.trim()){
      const list=el('ul',undefined,'search-list');filtered.forEach(n=>{const li=el('li');li.append(typeRow(n,{path:true}));list.append(li);});$('class-tree').append(list);
      if(!filtered.length)$('class-tree').append(el('p','일치하는 클래스·선언이 없습니다.','empty'));
    }else if(state.view==='folder')$('class-tree').append(treeList(model.folders(filtered)));
    else{
      $('class-tree').append(treeList(model.inheritance(filtered)));
      const other=filtered.filter(n=>n.kind==='namespace'||n.kind==='enum');
      if(other.length)$('class-tree').append(treeList([{kind:'data',label:'상속하지 않는 선언',children:other.map(n=>({kind:'type',name:n.name,label:n.name,children:[]}))}]));
    }
    $('tree-status').textContent=`${filtered.length} / ${data.nodes.length}개 선언${query.trim()?' · 검색 결과':''}`;
    $('folder-view').setAttribute('aria-pressed',String(state.view==='folder'));
    $('inheritance-view').setAttribute('aria-pressed',String(state.view==='inheritance'));
    $('view-hint').textContent=state.view==='folder'?'폴더 아래에 실제 선언을 배치했습니다. 클래스 아래 들여쓰기는 상속 관계입니다.':'부모 타입 → 자식 타입 순서입니다. 다중 상속의 나머지 부모는 세부 설명에 표시합니다.';
  }
  function declaration(field){
    const wrap=el('div',undefined,'declaration');wrap.append(external(field.url,field.declaration+' ↗'));
    for(const name of field.references){if(byName.has(name))wrap.append(button(name+' 설명 →',()=>select(name),'reference-button'));}
    for(const schema of field.schemas){const d=el('details',undefined,'nested-schema');d.append(el('summary',schema.name+' · 내부 데이터 '+schema.fields.length+'개'),button(schema.name+' 전체 설명 →',()=>select(schema.name)));schema.fields.forEach(f=>d.append(declaration(f)));wrap.append(d);}
    return wrap;
  }
  function related(title,names){
    const section=el('section',undefined,'relation-group');section.append(el('h4',title));
    for(const name of [...new Set(names)])section.append(byName.has(name)?button(name,()=>select(name),'relation-link'):el('span',name+' · 외부 타입','external-type'));
    return section;
  }
  function renderDetails(n){
    $('detail-label').textContent=n.name;$('selected-name').textContent=n.qualified;
    $('selected-meta').textContent=labels[n.kind]+' · '+n.path+':'+n.line;
    $('selected-purpose').textContent=n.purpose;$('selected-source').href=n.url;$('selected-source').hidden=false;$('selected-content').hidden=false;
    const fields=$('field-details');fields.scrollTop=0;window.PANDORA_MEMBER_INSPECTOR.render(n,fields,declaration);
    const relations=$('relation-details');relations.replaceChildren();relations.scrollTop=0;
    if(n.bases.length)relations.append(related('상속한 부모',n.bases));
    const derived=data.nodes.filter(c=>c.bases.includes(n.name));if(derived.length)relations.append(related('이 타입을 상속한 선언',derived.map(c=>c.name)));
    const refs=[...new Set(n.fields.flatMap(f=>f.references))].filter(name=>name!==n.name);if(refs.length)relations.append(related('멤버로 포함·참조하는 타입',refs));
    const usedBy=data.nodes.filter(c=>c.name!==n.name&&c.fields.some(f=>f.references.includes(n.name)));if(usedBy.length)relations.append(related('이 타입을 멤버로 사용하는 선언',usedBy.map(c=>c.name)));
    if(!relations.childElementCount)relations.append(el('p','헤더의 상속·멤버 타입 선언에서 연결된 프로젝트 타입이 없습니다.','data-note'));
    $('methods-summary').textContent=`선언된 함수 · ${n.methods.length}`;
    const methods=$('method-details');methods.replaceChildren();methods.scrollTop=0;
    for(const m of n.methods){const card=el('article',undefined,'method-card');card.append(el('small',m.access),external(m.url,m.declaration+' ↗'));if(m.comment)card.append(el('p',m.comment));methods.append(card);}
    if(!n.methods.length)methods.append(el('p','이 선언에서 직접 정의한 함수는 없습니다.','data-note'));
    const enums=$('enum-details');enums.replaceChildren();if(n.values.length){enums.append(el('h3','열거값'));for(const v of n.values)enums.append(external(v.url,v.declaration+' ↗'));}
  }
  function select(name,{push=true,scroll=true}={}){
    if(!byName.has(name))return;
    const changed=state.selected!==name;state.selected=name;renderDetails(byName.get(name));$('detail-disclosure').open=true;window.PANDORA_MEMBER_INSPECTOR.load();
    document.querySelectorAll('.type-name').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.name===name)));updateURL(push&&changed);
    if(scroll)requestAnimationFrame(()=>{$('detail-disclosure').scrollIntoView({block:'start',behavior:'smooth'});$('selected-name').focus({preventScroll:true});});
  }
  function view(mode){state.view=mode;renderTree();updateURL();}
  $('folder-view').onclick=()=>view('folder');$('inheritance-view').onclick=()=>view('inheritance');
  $('search').addEventListener('input',renderTree);$('kind-filter').addEventListener('change',renderTree);
  $('search').addEventListener('keydown',e=>{if(e.key==='Escape'){$('search').value='';renderTree();}});
  $('expand-all').onclick=()=>document.querySelectorAll('#class-tree details').forEach(d=>d.open=true);
  $('collapse-all').onclick=()=>document.querySelectorAll('#class-tree details').forEach(d=>d.open=false);
  $('back-to-tree').onclick=()=>{
    const selected=[...document.querySelectorAll('.type-name')].find(b=>b.dataset.name===state.selected);
    if(selected){let parent=selected.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}requestAnimationFrame(()=>{selected.scrollIntoView({block:'center',behavior:'instant'});selected.focus({preventScroll:true});});}
    else{$('tree-scroll').scrollIntoView({block:'start'});$('search').focus({preventScroll:true});}
  };
  // Selecting a class inside an inheritance summary must not collapse the branch.
  $('class-tree').addEventListener('click',e=>{if(e.target.closest('.type-name'))e.preventDefault();});
  addEventListener('popstate',()=>{const q=new URLSearchParams(location.search);state.view=q.get('view')==='inheritance'?'inheritance':'folder';state.selected=byName.has(q.get('class'))?q.get('class'):null;renderTree();if(state.selected)select(state.selected,{push:false,scroll:false});else{$('detail-disclosure').open=false;updateURL();}});
  $('tree-stats').textContent=`클래스 ${data.meta.counts.class} · 구조체 ${data.meta.counts.struct} · 기타 ${data.meta.counts.namespace+data.meta.counts.enum}`;
  $('source-summary').textContent=`전체 클래스 · UE ${data.meta.engine}`;
  $('revision').append(el('span','소스 기준 '+data.meta.sourceDate.slice(0,10)+' · '),external('https://github.com/wighs33/Pandora-Battle/tree/'+data.meta.commit,data.meta.commit.slice(0,12)+' ↗'));
  renderTree();
  const aliases={UPandoraSkillBinder:'FPandoraSkillBinder',ASword:'AMeleeWeapon',UProjectileAbility:'USkillProjectileCastAction',UPandoraInstance:'UPandoraComponent',UAbilityAttributeManager:'UPdAbilitySystemComponent'};
  const initial=aliases[params.get('class')]||params.get('class');
  if(byName.has(initial))select(initial,{push:false,scroll:false});else updateURL();
  if(embedded){let last=0;new ResizeObserver(()=>{const height=Math.ceil($('atlas').getBoundingClientRect().height);if(height!==last){last=height;parent.postMessage({type:'pandora-atlas-height',height:Math.max(500,Math.min(4800,height))},location.origin);}}).observe($('atlas'));}
})();
