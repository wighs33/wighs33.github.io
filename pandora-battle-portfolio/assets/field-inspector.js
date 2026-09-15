/* Detailed member documentation, separating direct use and verified Getter calls. */
(() => {
  'use strict';
  const modes={read:'읽기',write:'대입·변경',update:'내용 갱신',call:'메서드 호출',argument:'인자로 전달',return:'반환',replication:'복제 등록',notification:'복제 알림',attribute:'GAS 속성 식별'};
  let loading=null,failed=false,current=null,query='';
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const link=(url,text)=>{const a=el('a',text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;};
  function load(){
    if(window.PANDORA_FIELD_USAGE)return Promise.resolve();
    if(loading)return loading;
    failed=false;
    loading=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src='assets/field-usage-data.js?v=gas-3';
      script.onload=()=>{
        if(window.PANDORA_FIELD_USAGE?.meta.commit===window.PANDORA_CLASS_MAP.meta.commit)resolve();
        else{delete window.PANDORA_FIELD_USAGE;script.remove();reject(Error('Source revision mismatch'));}
      };
      script.onerror=()=>{script.remove();reject(Error('Member data unavailable'));};
      document.head.append(script);
    }).catch(()=>{failed=true;loading=null;}).then(()=>{if(current)render(current.node,current.target,current.declaration);});
    return loading;
  }
  function sourcePoint(fn,hit){return fn.url.replace(/#L\d+$/,'#L'+hit.line);}
  function functionCard(use,data,fieldKey){
    const fn=data.functions[use.function],row=el('article',undefined,'member-function');row.dataset.function=fn.owner+'::'+fn.name;
    const badges=el('div',undefined,'usage-badges');
    use.modes.forEach(mode=>badges.append(el('span',modes[mode]||mode,mode)));
    if(fn.context==='editor')badges.append(el('span','에디터·검증','context'));
    if(fn.context==='test')badges.append(el('span','테스트','context'));
    if(fn.generated)badges.append(el('span','매크로 생성','context'));
    if(use.access==='getter')badges.append(el('span','Getter 경유','getter'));
    row.append(badges,link(fn.url,(fn.owner?fn.owner+'::':'')+fn.name+'() ↗'));
    for(const via of use.via.filter(v=>v!=='ATTRIBUTE_ACCESSORS')){
      const getter=data.getters[via];
      if(getter){const route=el('p',undefined,'getter-route');route.append(el('span','이 함수 → '),link(getter.url,via+' ↗'),el('span',' → '+fieldKey));row.append(route);}
    }
    if(fn.comment&&!fn.generated)row.append(el('p',fn.comment,'function-purpose'));
    const hits=[...use.evidence].sort((a,b)=>Number(['write','update'].includes(b.mode))-Number(['write','update'].includes(a.mode))||a.line-b.line);
    function evidence(hit){const p=el('div',undefined,'member-evidence');p.append(el('code',hit.snippet),link(sourcePoint(fn,hit),'L'+hit.line+' ↗'));return p;}
    if(hits.length)row.append(evidence(hits[0]));
    if(hits.length>1){const more=el('details',undefined,'usage-more');more.append(el('summary',`사용 구문 ${hits.length-1}개 더 보기`));hits.slice(1).forEach(h=>more.append(evidence(h)));row.append(more);}
    return row;
  }
  function functionGroup(title,uses,data,fieldKey,{collapsed=false}={}){
    if(!uses.length)return null;
    const group=el(collapsed?'details':'section',undefined,'member-function-group');
    group.append(el(collapsed?'summary':'h4',`${title} · ${uses.length}`));
    const first=collapsed?uses:uses.slice(0,6);first.forEach(u=>group.append(functionCard(u,data,fieldKey)));
    if(!collapsed&&uses.length>6){const more=el('details',undefined,'usage-more');more.append(el('summary',`나머지 함수 ${uses.length-6}개 보기`));uses.slice(6).forEach(u=>more.append(functionCard(u,data,fieldKey)));group.append(more);}
    return group;
  }
  function memberCard(node,field,doc,data,declaration,open){
    const card=el('details',undefined,'member-card');card.dataset.member=field.key;card.open=open;
    const summary=el('summary'),head=el('span',undefined,'member-summary-heading');
    head.append(el('code',field.key),el('small',doc?`직접 ${doc.uses.filter(u=>u.access==='direct'&&!data.functions[u.function].generated).length} · Getter ${doc.uses.filter(u=>u.access==='getter').length}`:''));
    summary.append(head,el('span',doc?.purpose||field.declaration,'member-summary-purpose'));card.append(summary);
    const body=el('div',undefined,'member-body');
    body.append(el('h4','이 데이터를 갖고 있는 이유'),el('p',doc?.purpose||'함수 사용 데이터를 불러오면 보관 목적과 활용 위치가 표시됩니다.','member-purpose'));
    if(doc){
      const own=[],external=[],getters=[],other=[],generated=[];
      for(const use of doc.uses){const fn=data.functions[use.function];if(fn.generated)generated.push(use);else if(fn.context!=='runtime')other.push(use);else if(use.access==='getter')getters.push(use);else if(fn.owner===node.name)own.push(use);else external.push(use);}
      for(const group of [functionGroup('이 클래스에서 직접 활용',own,data,field.key),functionGroup('외부에서 필드에 직접 접근',external,data,field.key),functionGroup('Getter를 통한 활용',getters,data,field.key),functionGroup('에디터·테스트에서 활용',other,data,field.key,{collapsed:true}),functionGroup('GAS 매크로가 생성하는 접근자',generated,data,field.key,{collapsed:true})])if(group)body.append(group);
      if(!doc.uses.length)body.append(el('p','분석한 C++ 소스에서 이 멤버의 직접 사용이나 Getter 경유 사용 함수는 확인되지 않았습니다. Blueprint·리플렉션에서의 사용 여부는 이 목록에 포함하지 않습니다.','data-note'));
    }
    const raw=el('details',undefined,'member-declaration');raw.append(el('summary','실제 선언 · 하위 데이터'));raw.append(declaration(field));body.append(raw);
    card.append(body);return card;
  }
  function render(node,target,declaration){
    if(current?.node.name!==node.name)query='';
    current={node,target,declaration};target.replaceChildren();
    const data=window.PANDORA_FIELD_USAGE;
    target.append(el('p','직접 참조와 Getter를 통한 활용을 구분합니다. Getter 경유는 어떤 접근 함수를 호출했는지 함께 표시합니다. Setter만 호출하거나 더 먼 호출 단계를 거치는 함수는 포함하지 않습니다. 선언의 초기값은 C++ 기본값입니다.','data-note'));
    if(!node.fields.length){target.append(el('p','이 클래스가 직접 선언한 멤버변수는 없습니다.','data-note'));return;}
    if(!data){
      target.append(el('p',failed?'멤버 활용 데이터를 불러오지 못했습니다.':'멤버별 목적과 활용 함수를 불러오는 중…','member-loading'));
      if(failed){const retry=el('button','다시 불러오기');retry.type='button';retry.onclick=load;target.append(retry);}
      if(document.getElementById('detail-disclosure').open&&!loading&&!failed)load();
    }
    const tools=el('div',undefined,'member-search'),label=el('label','멤버변수 찾기'),input=el('input'),count=el('span',undefined,'member-count');
    input.type='search';input.placeholder='멤버 이름 · 보관 목적 · 함수 이름';input.value=query;input.setAttribute('aria-label','세부 설명의 멤버변수 찾기');label.append(input);tools.append(label,count);target.append(tools);
    const list=el('div',undefined,'member-list');target.append(list);
    function filter(){
      query=input.value;const words=query.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const found=node.fields.filter(field=>{const doc=data?.classes[node.name]?.[field.key],text=[field.key,field.declaration,doc?.purpose,...(doc?.uses||[]).map(u=>{const f=data.functions[u.function];return f.owner+' '+f.name;})].join(' ').toLowerCase();return words.every(w=>text.includes(w));});
      count.textContent=`${found.length} / ${node.fields.length}개 멤버`;list.replaceChildren(...found.map((field,i)=>memberCard(node,field,data?.classes[node.name]?.[field.key],data,declaration,i===0)));
      if(!found.length)list.append(el('p','일치하는 멤버변수가 없습니다.','data-note'));
    }
    input.addEventListener('input',filter);filter();
  }
  document.getElementById('detail-disclosure').addEventListener('toggle',()=>{if(document.getElementById('detail-disclosure').open)load();});
  window.PANDORA_MEMBER_INSPECTOR={render,load};
})();
