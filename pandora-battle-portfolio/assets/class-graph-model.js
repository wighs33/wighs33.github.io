/* Canonical class views and obstacle-aware orthogonal routing. No remote runtime. */
(() => {
  'use strict';
  const W=276, GAP=72, COL=W+GAP;
  // A row is a compact field group. Every key is checked against the source schema.
  const ROWS={
    APdPlayerState:['AbilitySystemComponent','BasicAttributeSet','PandoraComponent','PandoraTreeComponent','InventoryComponent','PlayerMatchComponent'],
    UPdAbilitySystemComponent:['GrantedPandoraSkillSources','ActivationsWaitingForSource','AbilityGrantAndInputManager','AttributeManager'],
    UPandoraSkillSource:['PandoraDefinition','SkillDataAsset','SkillIndex','PandoraLevel','LoadoutDirection'],
    UPandoraDefinition:['DisplayName,Description','IconTexture,IdTag','ActivatableWeaponTags','MaxLevel,PointsRequiredPerLevel','UnlockRules','Skill','Tier,ShopData'],
    USkillDefinition:['Name,Icon','ManaCost','Damage','Time','AbilitiesToGrant','ProjectileSettings','StatusEffectDataAsset'],
    UPandoraComponent:['AllPandoraList','CurrentPandoraDefinition','PandoraLoadoutSlots','GrantedPandoraAbilityHandles'],
    UPandoraTreeComponent:['GrantedPandoras','PointsAvailable','InitialGrantedPandoras,InitialPointsAvailable'],
    UPandoraInstance:['PandoraDefinition','IsOwned'],
    UBasicAttributeSet:['Health,MaxHealth','Mana,MaxMana','Stamina,MaxStamina','Level,Experience','Strength,Intelligence,Armor'],
    UInventoryComponent:['AllItemList','WeaponIdsByLoadoutSlot','ConsumableQuickSlotItemIds','EquippedItemSlots'],
    UItemInstance:['ItemDefinition','ItemId','Quantity,UpgradeLevel','Map_EnhancedStat_Magnitude'],
    UItemDefinition:['DisplayName,IdTag','Map_Stat_Magnitude','ConsumeGameplayEffectClass','WeaponData','ShopData'],
    UEquipmentComponent:['CurrentWeaponActor','CurrentWeaponDefinition','CurrentWeaponId','CurrentWeaponStatSnapshot'],
    UPdGameplayAbility:['CostAndCooldownManager','MovementManager','PresentationManager','ActiveSelfBuffEffectHandle'],
    APdPlayerController:['ControllerInputComponent','ControllerSessionComponent','ControllerProfileSyncComponent','PlayerControllerDefinition'],
    UControllerInputComponent:['LoadedInputDefinition','AppliedInputMapping','LoadedInputActions','BindingHandles'],
    UControllerInputDefinition:['InputMapping,Priority','MoveInputAction,LookInputAction','AttackInputAction,AimInputAction','Skill1InputAction,Skill2InputAction','CharacterActionDefinition'],
    UOnlineSessionsSubsystem:['SessionInterface','ActiveSessionSearch','ActiveSessionRequestId','ActiveSessionRequestKind,SessionOperationState','PendingRoomName,PendingMapName'],
    UPlayerProfileSubsystem:['SavedGameByPlayerId','SaveSnapshotsByPlayerId','DirtyPlayerIds,SaveInFlightPlayerIds','SaveDeadlinesByPlayerId'],
    UPdSaveGame:['SaveId,SaveRevision','Gold','PlayerPandoraData','PlayerSkinData','MatchRecords'],
    UProfileSaveEnvelope:['ProfileSaveId,ProfileRevision','PlainPayloadCrc','ObfuscatedPayload'],
    AExperienceGameMode:['MatchFlowComponent','SpawnComponent','PlayerProvisioningComponent','MatchRuleDefinition'],
    AExperienceGameState:['ExperienceManagerComponent','MatchRuleDefinition','MatchTimerState'],
    UExperienceManagerComponent:['CurrentExperienceId','CurrentExperience','LoadState','GameFeaturePluginURLs'],
    UExperienceDefinition:['DefaultPawnClass','GameFeaturesToEnable'],
    APdPlayer:['PlayerPawnDefinition','CombatComponent'],
    ACharacterBase:['CharacterDefinition','EquipmentComponent','CharacterDeathComponent','StatusEffectReplicationComponent'],
    AEnemyBase:['EnemyDefinition','AbilitySystemComponent','EnemyCombatComponent','EnemyTrainingBotComponent'],
    UEnemyBaseDefinition:['Combat','TrainingBot','MonsterStateTree','MonsterMaxHealth'],
    APdHUD:['UiRouter','WidgetClassDefinition','CachedPlayerHUD','CachedInfoUiPresenter'],
    UHudUiRouter:['OwnerHud','ActiveDefinition','MenuLayer','ScreenLayer','ScoreboardLayer'],
    UInfoLoadoutStore:['BoundInventoryComponent','BoundPandoraComponent','LeftWeapon,UpWeapon,RightWeapon','LeftPandora,UpPandora,RightPandora'],
    UInfoUiPresenter:['LoadoutStore','StatusPresenter','ItemPresenter','PandoraPresenter'],
    UPandoraDescriptionWidget:['PandoraDefinition','PandoraTreeComponent','PandoraDescriptionViewModel'],
    ALobbyGameMode:['MatchCoordinator','TravelCoordinator','DefaultPlayerProvisioner'],
    ALobbyGameState:['ExperienceManagerComponent','SelectedMapOption','bStartPending','GameStartEndServerTimeSeconds'],
    UCombatComponent:['CombatDamageSettings','UnarmedCombatSettings','HitActorsInCurrentUnarmedAttack','ActiveComboDamageMultiplier']
  };
  const NESTED={
    'UPandoraDefinition.UnlockRules':[['RequiredPandora','RequiredLevel']],
    'UPandoraDefinition.Skill':[['SkillDefinition']],
    'UPandoraTreeComponent.GrantedPandoras':[['Pandora','Level']],
    'USkillDefinition.Time':[['CooldownDuration','Duration']],
    'USkillDefinition.Damage':[['GameplayEffectClass','Magnitude']],
    'UItemDefinition.WeaponData':[['Equip','Attack','Movement']],
    'UPdSaveGame.PlayerPandoraData':[['GrantedPandorasById'],['SelectedPandoraId','PandoraPoints'],['PandoraLoadoutByDirectionId']]
  };
  // Shared objects appear once per view. Other core nodes open their canonical view.
  const VIEWS={
    APdPlayerState:[['APdPlayerState',0,0],['UPdAbilitySystemComponent',1,0],['UBasicAttributeSet',2,0],['UPandoraComponent',0,290],['UPandoraSkillSource',1,290],['UInventoryComponent',2,290],['UPandoraTreeComponent',0,580],['UPandoraDefinition',1,580]],
    APdPlayerController:[['APdPlayerController',1,0],['UPlayerControllerDefinition',0,0],['UPdGameInstanceDefinition',2,0],['UControllerInputComponent',0,290],['UControllerSessionComponent',1,290],['UControllerProfileSyncComponent',2,290],['UControllerInputDefinition',0,560],['UOnlineSessionsSubsystem',1,560],['UPlayerProfileSubsystem',2,560]],
    UPdAbilitySystemComponent:[['UPdAbilitySystemComponent',1,0],['FPandoraSkillBinder',0,0],['UAbilityGrantAndInputManager',0,250],['UPandoraSkillSource',1,250],['UPandoraDefinition',2,250],['UAbilityAttributeManager',0,560],['UPdGameplayAbility',1,560],['USkillDefinition',2,620]],
    UPandoraSkillSource:[['UPdAbilitySystemComponent',1,0],['FPandoraSkillBinder',0,0],['UPdGameplayAbility',2,0],['UPandoraSkillSource',1,260],['UPandoraDefinition',0,540],['USkillDefinition',2,540]],
    UPandoraDefinition:[['UPandoraSkillSource',0,0],['UPandoraTreeComponent',1,0],['UPandoraComponent',2,0],['UPandoraDefinition',1,280],['UPandoraDescriptionWidget',0,590],['USkillDefinition',1,620],['UPandoraDescriptionViewModel',2,590]],
    UPandoraComponent:[['USelectingPandoraAndWeaponComponent',0,0],['UPandoraComponent',1,0],['UPandoraInstance',0,270],['UPandoraDefinition',1,270],['UPandoraTreeComponent',2,270],['FPandoraSkillBinder',0,600],['USkillDefinition',1,610],['UPandoraSkillSource',2,600]],
    UInventoryComponent:[['APdPlayerState',0,0],['UInventoryComponent',1,0],['USelectingPandoraAndWeaponComponent',2,0],['UItemInstance',1,280],['UEquipmentComponent',2,280],['UItemDefinition',1,540],['AWeaponBase',2,560]],
    APdPlayer:[['APdPlayer',1,0],['APdPlayerState',0,230],['ACharacterBase',1,230],['UPlayerPawnDefinition',2,230],['UEquipmentComponent',0,540],['UCharacterDeathComponent',1,540],['UStatusEffectReplicationComponent',2,540]],
    UPdGameplayAbility:[['UPandoraSkillSource',0,0],['UPdGameplayAbility',1,0],['UAttackAbility',2,0],['USkillDefinition',0,280],['UAbilityCostAndCooldownManager',1,280],['UAbilityPresentationManager',2,280],['UProjectileAbility',1,610],['AProjectileBase',2,610]],
    UPlayerProfileSubsystem:[['UControllerProfileSyncComponent',0,0],['UPlayerProfileSubsystem',1,0],['UExperiencePlayerProfileService',2,0],['UPdSaveGame',0,280],['UProfileSaveEnvelope',2,280]],
    AExperienceGameMode:[['AExperienceGameMode',1,0],['UMatchRuleDefinition',0,0],['ULevelDefinition',2,0],['UExperienceMatchFlowComponent',0,260],['UExperienceSpawnComponent',1,260],['UExperiencePlayerProvisioningComponent',2,260],['UExperiencePlayerProfileService',1,540],['UDefaultPlayerProvisioner',2,540]],
    UExperienceManagerComponent:[['AExperienceGameState',0,0],['UExperienceManagerComponent',1,260],['ALobbyGameState',2,0],['UExperienceDefinition',1,530]],
    ALobbyGameMode:[['ALobbyGameMode',1,0],['ULobbyMatchCoordinator',0,260],['ULobbyTravelCoordinator',1,260],['ULobbyConfigurationComponent',2,260],['UOnlineSessionsSubsystem',0,520],['ULevelDefinition',2,520],['UDefaultPlayerProvisioner',0,0]],
    AEnemyBase:[['AMonsterCharacter',0,0],['AEnemyBase',1,0],['AMonsterAIController',2,0],['UPdAbilitySystemComponent',0,280],['UEnemyBaseDefinition',1,280],['UEnemyTrainingBotComponent',2,280],['UEnemyCombatComponent',1,590],['UItemDefinition',2,590]],
    APdHUD:[['APdHUD',1,0],['UHudUiRouter',0,260],['UInfoUiPresenter',1,260],['UWidgetClassDefinition',2,260],['UUiSubsystem',0,570],['UInfoLoadoutStore',1,570],['UInfoPandoraTabPresenter',2,570]],
    UInfoLoadoutStore:[['UInfoUiPresenter',0,0],['UInfoLoadoutStore',1,0],['UInfoPandoraTabPresenter',2,0],['UInventoryComponent',0,280],['UPandoraComponent',2,280],['UItemInstance',0,550],['UPandoraDefinition',1,550],['UPandoraInstance',2,550]]
  };
  const cleanType=s=>s.replace(/\b(?:const|mutable|static)\s+/g,'').replace(/T(?:WeakObjectPtr|ObjectPtr|SoftObjectPtr|SoftClassPtr)<(.+)>/g,'$1*').replace(/TArray<(.+)>/g,'$1[]').replace(/TMap<.+>/g,'Map').replace(/TSet<.+>/g,'Set').replace(/FGameplayAttributeData/g,'Attribute').replace(/FGameplayTagContainer/g,'Tags').replace(/FGameplayTag/g,'Tag');
  function typeOf(f){return cleanType(f.declaration.slice(0,f.declaration.search(new RegExp('\\b'+f.key+'\\b'))).trim());}
  function makeRows(n){
    const byKey=new Map(n.fields.map(f=>[f.key,f]));
    const selected=ROWS[n.name] || n.highlights.slice(0,5).map(h=>h.keys.slice(0,2).join(','));
    const groups=selected.flatMap(group=>group.length>34?group.split(','):group);
    const rows=[];
    for(const raw of groups){
      const keys=raw.split(','),fields=keys.map(k=>byKey.get(k));
      if(fields.some(f=>!f))throw Error(`Unknown UML field: ${n.name}.${raw}`);
      const meaning=n.highlights.find(h=>h.keys.some(k=>keys.includes(k)))?.meaning||n.role;
      const nested=NESTED[n.name+'.'+keys[0]];
      rows.push({keys,fields,label:keys.join(' · '),type:keys.length===1?typeOf(fields[0]):'',meaning,nested:false});
      if(nested){
        const children=fields[0].schemas.flatMap(s=>s.fields);
        for(const childKeys of nested){
          const childFields=childKeys.map(k=>children.find(f=>f.key===k));
          if(childFields.some(f=>!f))throw Error(`Unknown nested UML field: ${n.name}.${childKeys}`);
          rows.push({keys:childKeys,fields:childFields,label:childKeys.join(' · '),type:childKeys.length===1?typeOf(childFields[0]):'',meaning,nested:true,parent:keys[0]});
        }
      }
    }
    return rows;
  }
  function containsReference(field,name){return field.references.includes(name)||field.schemas.some(s=>s.fields.some(f=>containsReference(f,name)));}
  function fieldRow(n,e){
    const field=n.fields.find(f=>containsReference(f,e.target));
    return field?n.rows.findIndex(r=>r.keys.includes(field.key)):-1;
  }
  function buildView(data,root,expanded=false,landscape=false){
    const byName=new Map(data.nodes.map(n=>[n.name,n]));
    if(!byName.has(root))throw Error('Unknown graph root: '+root);
    const incident=data.edges.filter(e=>e.source===root||e.target===root);
    let spec=VIEWS[root];
    if(!spec||expanded){
      const neighbors=[...new Set(incident.filter(e=>e.source===root).map(e=>e.target).concat(incident.filter(e=>e.target===root).map(e=>e.source)))];
      const chosen=neighbors.slice(0,expanded?18:8);
      const slots=[[1,0],[0,0],[2,0],[0,280],[2,280],[1,570],[0,570],[2,570]];
      spec=[[root,1,280],...chosen.map((name,i)=>[name,...(slots[i]||[i%3,850+Math.floor((i-8)/3)*280])])];
    }
    const names=new Set(spec.map(s=>s[0]));
    if(names.size!==spec.length)throw Error('Duplicate UML block in '+root);
    const nodes=spec.map(([name,col,y])=>{
      const n=byName.get(name);if(!n)throw Error('Missing UML class '+name);
      const rows=makeRows(n);
      return {...n,rows,x:col*COL,y,width:W,height:76+Math.max(rows.length,1)*22};
    });
    // Variable-height UML compartments must leave room for routing channels.
    for(const x of new Set(nodes.map(n=>n.x))){
      let bottom=-80;
      nodes.filter(n=>n.x===x).sort((a,b)=>a.y-b.y).forEach(n=>{n.y=Math.max(n.y,bottom+80);bottom=n.y+n.height;});
    }
    if(landscape){
      const wideOrder={
        APdPlayerState:['APdPlayerState','UPdAbilitySystemComponent','UPandoraSkillSource','UPandoraDefinition','UPandoraComponent','UPandoraTreeComponent','UBasicAttributeSet','UInventoryComponent'],
        UPdAbilitySystemComponent:['UPdAbilitySystemComponent','UPandoraSkillSource','UPandoraDefinition','USkillDefinition','FPandoraSkillBinder','UAbilityGrantAndInputManager','UAbilityAttributeManager','UPdGameplayAbility'],
        UPandoraComponent:['UPandoraComponent','UPandoraInstance','UPandoraDefinition','USkillDefinition','USelectingPandoraAndWeaponComponent','UPandoraTreeComponent','FPandoraSkillBinder','UPandoraSkillSource']
      };
      const order=!expanded&&wideOrder[root]||nodes.map(n=>n.name),cols=Math.min(5,Math.ceil(nodes.length/2));
      let top=0;
      for(let i=0;i<order.length;i+=cols){
        const row=order.slice(i,i+cols).map(name=>nodes.find(n=>n.name===name));
        row.forEach((n,j)=>{n.x=j*COL;n.y=top;});top+=Math.max(...row.map(n=>n.height))+100;
      }
    }
    const edges=data.edges.filter(e=>names.has(e.source)&&names.has(e.target));
    const countShown=incident.filter(e=>names.has(e.source)&&names.has(e.target)).length;
    return {root,nodes,edges,hiddenConnections:incident.length-countShown,expanded};
  }
  function overlap(a,b,pad=0){return a.x<b.x+b.width+pad&&a.x+a.width+pad>b.x&&a.y<b.y+b.height+pad&&a.y+a.height+pad>b.y;}
  class Heap{
    constructor(){this.a=[];}
    push(n){const a=this.a;a.push(n);let i=a.length-1;while(i){const p=(i-1)>>1;if(a[p].f<=n.f)break;a[i]=a[p];i=p;}a[i]=n;}
    pop(){const a=this.a,first=a[0],last=a.pop();if(a.length){let i=0;while(i*2+1<a.length){let c=i*2+1;if(c+1<a.length&&a[c+1].f<a[c].f)c++;if(a[c].f>=last.f)break;a[i]=a[c];i=c;}a[i]=last;}return first;}
  }
  function routeView(view){
    const nodes=new Map(view.nodes.map(n=>[n.name,n]));
    for(let i=0;i<view.nodes.length;i++)for(let j=i+1;j<view.nodes.length;j++)if(overlap(view.nodes[i],view.nodes[j],12))throw Error(`UML blocks overlap: ${view.root}: ${view.nodes[i].name}/${view.nodes[j].name}`);
    const side=(a,b)=>Math.abs(b.x-a.x)>W*.55?(b.x>a.x?'E':'W'):(b.y>a.y?'S':'N');
    const endpoints=view.edges.map(e=>{
      const a=nodes.get(e.source),b=nodes.get(e.target);
      return {e,a,b,sourceSide:side(a,b),targetSide:side(b,a),row:fieldRow(a,e)};
    });
    const ports=new Map();
    for(const p of endpoints)for(const end of ['source','target']){
      const n=end==='source'?p.a:p.b,key=n.name+':'+end+':'+p[end+'Side'];
      if(!ports.has(key))ports.set(key,[]);ports.get(key).push(p);
    }
    function port(p,end){
      const n=end==='source'?p.a:p.b,s=p[end+'Side'],group=ports.get(n.name+':'+end+':'+s);
      group.sort((a,b)=>(end==='source'?a.b.x-b.b.x:a.a.x-b.a.x)||a.e.id.localeCompare(b.e.id));
      const i=group.indexOf(p),spread=(i-(group.length-1)/2)*12;
      let x=n.x+n.width/2,y=n.y+n.height/2;
      if(s==='N'||s==='S'){x+=spread;y=s==='N'?n.y:n.y+n.height;}
      else{x=s==='W'?n.x:n.x+n.width;y=end==='source'&&p.row>=0?n.y+52+p.row*22:n.y+Math.max(8,Math.min(n.height-8,24+spread));}
      const anchor={x,y};
      const stub={x:x+(s==='W'?-24:s==='E'?24:0),y:y+(s==='N'?-24:s==='S'?24:0)};
      return {anchor,stub,side:s};
    }
    const links=endpoints.map(p=>({...p,from:port(p,'source'),to:port(p,'target')}));
    const xs=new Set(),ys=new Set();
    for(const n of view.nodes){
      [n.x-48,n.x-24,n.x+n.width/2,n.x+n.width+24,n.x+n.width+48].forEach(x=>xs.add(x));
      [n.y-48,n.y-24,n.y+n.height+24,n.y+n.height+48].forEach(y=>ys.add(y));
    }
    links.forEach(p=>[p.from.stub,p.to.stub].forEach(q=>{xs.add(q.x);ys.add(q.y);}));
    const X=[...xs].sort((a,b)=>a-b),Y=[...ys].sort((a,b)=>a-b),nx=X.length;
    const coord=id=>({x:X[id%nx],y:Y[Math.floor(id/nx)]});
    const index=q=>Y.indexOf(q.y)*nx+X.indexOf(q.x);
    const obstacles=view.nodes.map(n=>({x:n.x-12,y:n.y-12,width:n.width+24,height:n.height+24}));
    const clear=(a,b)=>!obstacles.some(r=>a.x===b.x?a.x>r.x&&a.x<r.x+r.width&&Math.max(a.y,b.y)>r.y&&Math.min(a.y,b.y)<r.y+r.height:a.y>r.y&&a.y<r.y+r.height&&Math.max(a.x,b.x)>r.x&&Math.min(a.x,b.x)<r.x+r.width);
    const blocked=new Set();
    for(let j=0;j<Y.length;j++)for(let i=0;i<X.length;i++)if(obstacles.some(r=>X[i]>r.x&&X[i]<r.x+r.width&&Y[j]>r.y&&Y[j]<r.y+r.height))blocked.add(j*nx+i);
    const adjacency=new Map(),reserved=new Map(),usedPoints=new Map();
    const segmentKey=(a,b)=>a<b?a+':'+b:b+':'+a;
    function neighbors(id){
      if(adjacency.has(id))return adjacency.get(id);
      const x=id%nx,y=Math.floor(id/nx),a=coord(id),out=[];
      for(const b of [x? id-1:-1,x<nx-1?id+1:-1,y?id-nx:-1,y<Y.length-1?id+nx:-1])if(b>=0&&!blocked.has(b)&&clear(a,coord(b)))out.push(b);
      adjacency.set(id,out);return out;
    }
    function route(a,b){
      const start=index(a),end=index(b),heap=new Heap(),dist=new Map(),prev=new Map();
      const heuristic=id=>{const q=coord(id);return Math.abs(q.x-b.x)+Math.abs(q.y-b.y);};
      heap.push({id:start,dir:0,g:0,f:heuristic(start),key:start*3});dist.set(start*3,0);
      let finish;
      while(heap.a.length){
        const cur=heap.pop();if(cur.g!==dist.get(cur.key))continue;
        if(cur.id===end){finish=cur.key;break;}
        const p=coord(cur.id);
        for(const id of neighbors(cur.id)){
          const q=coord(id),dir=p.x===q.x?2:1,key=id*3+dir,len=Math.abs(p.x-q.x)+Math.abs(p.y-q.y);
          const occupied=reserved.get(segmentKey(cur.id,id))||0;
          const cross=(usedPoints.get(id)||0)&(dir===1?2:1);
          const g=cur.g+len+(cur.dir&&cur.dir!==dir?80:0)+(occupied?len*3+70:0)+(cross?30:0);
          if(g>=(dist.get(key)??Infinity))continue;
          dist.set(key,g);prev.set(key,cur.key);heap.push({id,dir,key,g,f:g+heuristic(id)});
        }
      }
      if(finish===undefined)throw Error('No orthogonal route in '+view.root);
      const ids=[];for(let k=finish;k!==undefined;k=prev.get(k))ids.push(Math.floor(k/3));ids.reverse();
      ids.forEach((id,i)=>{if(!i)return;const last=ids[i-1],dir=coord(last).x===coord(id).x?2:1;reserved.set(segmentKey(last,id),(reserved.get(segmentKey(last,id))||0)+1);usedPoints.set(id,(usedPoints.get(id)||0)|dir);});
      return ids.map(coord);
    }
    const routed=[];
    // Short local relationships reserve clear channels before longer cross-branch links.
    links.sort((a,b)=>(Math.abs(a.a.x-a.b.x)+Math.abs(a.a.y-a.b.y))-(Math.abs(b.a.x-b.b.x)+Math.abs(b.a.y-b.b.y))||a.e.id.localeCompare(b.e.id));
    for(const p of links){
      const raw=[p.from.anchor,...route(p.from.stub,p.to.stub),p.to.anchor],points=[];
      for(const q of raw){if(points.length>=2){const a=points[points.length-2],b=points[points.length-1];if(a.x===b.x&&b.x===q.x||a.y===b.y&&b.y===q.y)points.pop();}points.push(q);}
      routed.push({...p.e,points,sourceRow:p.row});
    }
    const all=view.nodes.flatMap(n=>[{x:n.x,y:n.y},{x:n.x+n.width,y:n.y+n.height}]).concat(routed.flatMap(e=>e.points));
    const minX=Math.min(...all.map(p=>p.x))-36,minY=Math.min(...all.map(p=>p.y))-36;
    const width=Math.max(...all.map(p=>p.x))-minX+36,height=Math.max(...all.map(p=>p.y))-minY+36;
    return {...view,edges:routed,bounds:{x:minX,y:minY,width,height}};
  }
  function roundedPath(points){
    let d=`M${points[0].x},${points[0].y}`;
    for(let i=1;i<points.length-1;i++){
      const a=points[i-1],b=points[i],c=points[i+1];
      const l1=Math.abs(a.x-b.x)+Math.abs(a.y-b.y),l2=Math.abs(c.x-b.x)+Math.abs(c.y-b.y),r=Math.min(7,l1/2,l2/2);
      const pre={x:b.x+(a.x-b.x)/l1*r,y:b.y+(a.y-b.y)/l1*r},post={x:b.x+(c.x-b.x)/l2*r,y:b.y+(c.y-b.y)/l2*r};
      d+=` L${pre.x},${pre.y} Q${b.x},${b.y} ${post.x},${post.y}`;
    }
    const p=points[points.length-1];return d+` L${p.x},${p.y}`;
  }
  window.PANDORA_UML={buildView,routeView,roundedPath,makeRows,views:VIEWS,rows:ROWS};
})();
