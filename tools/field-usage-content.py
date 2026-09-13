"""Field-level intent, with explicit notes for easily misunderstood data ownership."""
import re

NOTES = '''
APdPlayerState.AbilitySystemComponent|플레이어의 능력·효과·속성을 실행하는 ASC를 PlayerState 수명에 연결해 둡니다. 캐릭터와 입력·소모품 처리에서 같은 실행기에 접근하도록 반환합니다.
APdPlayerState.BasicAttributeSet|체력·마나·레벨 등 GAS 속성의 저장 객체를 PlayerState의 기본 서브오브젝트로 생성해 유지합니다. 이 포인터의 직접 사용은 생성자이며, 실제 수치 처리는 UBasicAttributeSet과 GAS 쪽에서 이뤄집니다.
APdPlayerState.SelectingPandoraAndWeaponComponent|현재 무기와 판도라를 같은 로드아웃 방향으로 전환할 담당 컴포넌트를 유지하고, 선택 요청과 슬롯 변경 처리에서 꺼내 쓰게 합니다.
APdPlayerState.PlayerMatchComponent|플레이어의 매치 식별 정보를 조회·변경할 컴포넌트를 유지합니다. PlayerState 교체 시 CopyProperties에서 식별 정보를 새 객체로 인계합니다.
APdPlayerState.LobbyPlayerStateComponent|로비 이탈 여부와 닉네임·팀 관련 처리를 담당하는 컴포넌트를 유지해 로비 인원 집계와 사용자 표시에서 조회하게 합니다.
APdPlayerState.LevelingComponent|획득한 경험치를 레벨 상승과 포인트 지급으로 처리할 담당 컴포넌트를 연결해 둡니다.
APdPlayerState.SkinComponent|보유 스킨·외형 관련 데이터에 접근할 컴포넌트를 유지해 기본 지급, 보상과 프로필 동기화에 사용합니다.
APdPlayerState.InventoryComponent|아이템 소유 목록과 무기·소모품 슬롯에 접근할 인벤토리를 유지해 지급, 장착과 UI 갱신이 같은 목록을 사용하게 합니다.
APdPlayerState.PandoraComponent|보유 판도라·장착 슬롯·현재 선택을 관리하는 컴포넌트를 유지합니다. 보상·장착·스킬 발동과 UI가 같은 선택 상태를 조회하게 합니다.
APdPlayerState.PandoraTreeComponent|판도라별 성장 레벨과 남은 포인트를 관리하는 트리를 유지해 기본 지급, 성장과 선택 스킬의 실행 레벨 조회에 사용합니다.
APdPlayerState.PlayerRewardComponent|획득·처치 보상을 실제 플레이어 데이터에 지급할 담당 컴포넌트를 연결해 둡니다.
APdPlayerState.StatUpgradeComponent|스탯 기본값 적용과 투자·회수 요청을 처리할 컴포넌트를 유지합니다. BeginPlay에서 서버 기본 속성값을 적용할 때 사용합니다.
UPdAbilitySystemComponent.GrantedPandoraSkillSources|AbilitySpec이 참조하는 판도라 출처 객체를 유지하고 복제 서브오브젝트로 등록합니다. 더 이상 사용하는 능력이 없을 때 보관·복제 등록을 정리하기 위한 목록입니다.
UPdAbilitySystemComponent.ActivationsWaitingForSource|클라이언트에 판도라 출처가 아직 도착하지 않은 발동을 보류합니다. 출처 복제 후 재시도하고 종료·실패한 발동은 대기 목록에서 제거합니다.
UPdAbilitySystemComponent.AbilityGrantAndInputManager|능력 부여와 입력 태그·핸들 상태 처리를 한 관리자로 위임해 ASC의 입력/능력 콜백에서 재사용합니다.
UPdAbilitySystemComponent.AttributeManager|속성 설정 적용과 해제 수명을 담당하는 관리자를 유지해 ASC의 설정 요청을 위임합니다.
UPandoraSkillSource.PandoraDefinition|부여된 능력이 어느 판도라에서 왔는지 기억합니다. 원본의 스킬 슬롯을 찾고 판도라별 쿨다운을 구분하며, 플레이어의 현재 선택이 바뀌어도 출처를 유지합니다.
UPandoraSkillSource.SkillDataAsset|이 능력에 부여된 실제 스킬 설정을 기억해 비용·피해·시간·연출 설정을 읽을 수 있게 합니다. 판도라 전체 정의와 스킬 하나의 정의를 구분하는 참조입니다.
UPandoraSkillSource.SkillIndex|PandoraDefinition.Skill 배열에서 이 능력의 출처 슬롯을 식별합니다. 해당 슬롯 조회와 판도라/슬롯 조합의 쿨다운 구분에 사용합니다.
UPandoraSkillSource.PandoraLevel|출처 초기화 시 전달된 레벨을 보관합니다. Binder 경로에서는 스킬 슬롯의 요구 레벨을 전달하므로 Tree에 저장된 플레이어의 현재 성장 레벨과 같은 뜻으로 해석하지 않습니다.
UPandoraSkillSource.LoadoutDirection|능력이 어느 로드아웃 방향에서 부여됐는지 기억해 해당 방향의 판도라 속성 및 피해 계산 문맥을 선택할 때 사용합니다.
UPandoraDefinition.DisplayName|카드·슬롯·상점·설명 화면에서 사용할 판도라 이름입니다. GetDisplayName은 값이 비어 있으면 에셋 이름을 대신 반환합니다.
UPandoraDefinition.Description|판도라의 설명 원문을 보관해 카드·상점·상세 설명용 표시 데이터로 전달합니다.
UPandoraDefinition.IconTexture|판도라를 그림으로 식별할 공통 아이콘 에셋을 참조합니다. 슬롯·장착 버튼·보상 알림에서 같은 아이콘을 사용합니다.
UPandoraDefinition.IdTag|판도라의 종류를 태그로 식별해 종류별 검색·필터와 설정 검증에 사용합니다.
UPandoraDefinition.ActivatableWeaponTags|사용을 허용할 무기 태그들을 보관합니다. 무기 호환 여부를 검사하고 UI에 무기 요구 조건을 표시할 때 읽습니다.
UPandoraDefinition.MaxLevel|에셋의 최대 단계를 고정 규칙 3에 맞춰 정규화·검증하기 위한 필드입니다. 현재 GetMaxLevel은 이 필드를 읽지 않고 FixedPandoraMaxLevel 상수를 반환합니다.
UPandoraDefinition.PointsRequiredPerLevel|각 단계의 판도라 성장에 필요한 포인트 비용입니다. 레벨별 비용 조회에 쓰며, 정규화할 때 항목 수와 최소 비용을 보정합니다.
UPandoraDefinition.UnlockRules|선행 판도라와 필요한 성장 레벨을 저장합니다. Tree가 해금 가능 여부를 검사하고 설명 화면이 선행 조건을 안내할 때 사용합니다.
UPandoraDefinition.Skill|각 슬롯의 USkillDefinition 참조를 보관합니다. Binder가 능력을 부여하고 SkillSource가 원본 슬롯을 찾으며 스킬바·설명 화면이 슬롯 정보를 구성할 때 읽습니다.
UPandoraDefinition.Tier|에셋에 판도라 티어 분류를 기록합니다. 현재 확인된 직접 C++ 사용은 에디터 설정 검증이며, 런타임 성장 계산에 쓰인다고 단정하지 않습니다.
UPandoraDefinition.ShopData|판도라 상품의 가격·판매 관련 공통 설정을 담아 상점 상품 정보 조회와 에셋 유효성 검증에 사용합니다.
UPandoraTreeComponent.GrantedPandoras|플레이어가 성장시킨 판도라와 현재 레벨을 함께 저장합니다. 해금 조건·현재 레벨 조회, 성장 갱신과 저장/복원에 사용합니다.
UPandoraTreeComponent.PointsAvailable|현재 소비 가능한 판도라 포인트를 유지합니다. 성장 비용을 지불할 수 있는지 검사하고 획득·소비 후 화면에 남은 수량을 알립니다.
UPandoraTreeComponent.InitialGrantedPandoras|트리 초기 구성 시 지급할 판도라와 시작 레벨을 설정합니다. 실행 중 성장 기록인 GrantedPandoras와 구분합니다.
UPandoraTreeComponent.InitialPointsAvailable|트리 초기 구성에 사용할 시작 포인트 수량입니다. 실행 중 잔액인 PointsAvailable의 초기 정책을 제공합니다.
UPandoraComponent.AllPandoraList|판도라 정의와 플레이어의 보유 여부를 모아 소유 조회·획득·필터·로드아웃 검증에 사용합니다.
UPandoraComponent.CurrentPandoraDefinition|현재 선택한 판도라 정의를 참조해 선택 스킬의 부여·입력 연결과 UI 알림에 사용합니다.
UPandoraComponent.PandoraLoadoutSlots|로드아웃 방향별 판도라 정의를 보관해 방향 전환 시 어느 판도라를 선택할지 결정합니다.
UPandoraComponent.GrantedPandoraAbilityHandles|선택 판도라로 ASC에 부여한 능력 핸들을 추적해 선택 변경·재부여 시 기존 능력을 정리할 수 있게 합니다.
UPandoraComponent.AllPandroaDefinition|조회한 판도라 정의들을 모아 보유 목록 준비와 판도라 분류에 재사용합니다. 원본 코드의 Pandroa 철자를 그대로 표시합니다.
APdPlayerController.ControllerInputComponent|입력 정의 로드·매핑·액션 바인딩을 맡길 컴포넌트를 유지해 컨트롤러의 입력 설정 수명과 연결합니다.
APdPlayerController.ControllerSessionComponent|방 나가기와 세션 종료 절차를 담당하는 컴포넌트를 유지해 종료 요청을 위임합니다.
APdPlayerController.ControllerProfileSyncComponent|로컬 외형 프로필을 서버에 제출하고 적용하는 절차를 담당할 컴포넌트를 유지합니다.
APdPlayerController.ControllerPresentationComponent|알림·결과·로딩 등 화면 표현 요청을 실제 UI로 전달할 담당 컴포넌트를 유지합니다.
APdPlayerController.ChatControllerComponent|채팅 입력과 메시지 처리를 담당할 컴포넌트를 컨트롤러 수명에 연결합니다.
APdPlayerController.NotificationComponent|획득 보상 등 플레이어 알림을 표시할 담당 컴포넌트를 유지합니다.
APdPlayerController.PlayerControllerDefinition|컨트롤러의 화면 표현 설정 에셋을 소프트 참조로 지정해 필요할 때 로드하고 적용합니다.
APdPlayerController.LoadedPlayerControllerDefinition|로드 완료된 컨트롤러 설정을 유지해 이후 설정 적용에서 다시 로드하지 않고 읽습니다.
UPdGameInstanceDefinition.Memo|설정 에셋에 사람이 읽을 메모를 남기는 편집용 값입니다. 이 필드를 사용하는 C++ 실행 함수는 확인되지 않습니다.
ULobbyRuntimeSubsystem.LobbyDataAssetsPreloadHandle|로비 데이터 에셋 미리 읽기 요청을 보관할 핸들로 선언되어 있습니다. 현재 소스에는 이 멤버를 사용하는 함수가 확인되지 않습니다.
ULobbyRuntimeSubsystem.bLobbyDataAssetsPreloadPending|로비 데이터 에셋 로드 대기 상태용으로 선언된 플래그입니다. 현재 소스에는 이 멤버를 사용하는 함수가 확인되지 않습니다.
ULobbyRuntimeSubsystem.bLobbyDataAssetsReady|로비 데이터 에셋 준비 상태용으로 선언된 플래그입니다. 현재 소스에는 이 멤버를 사용하는 함수가 확인되지 않습니다.
UBasicAttributeSet.bLastOutgoingDamageCriticalHit|마지막으로 계산한 가하는 피해의 치명타 여부를 다음 소비 시점까지 유지하고, 소비 후 초기화합니다.
UBasicAttributeSet.bPendingIncomingDamageCriticalHit|받는 피해를 처리할 때 사용할 치명타 여부를 피해 실행 전후로 전달합니다.
UBasicAttributeSet.bPendingIncomingDamageAllowHitReact|대기 중인 받는 피해가 피격 반응을 허용하는지 보관해 피해 적용 시 반응 여부를 결정합니다.
UItemInstance.UpgradeStatBonusRatePerLevel|강화 레벨당 추가 스탯 비율을 보관해 강화 단계에 따른 아이템 능력치 보너스를 계산합니다.
UItemDefinition.bCanDropFromRewardChest|보상 상자의 드롭 후보에 이 아이템을 넣을지 결정하는 설정입니다.
UItemDefinition.DropRate|보상 아이템 선택에 사용할 드롭 확률/가중 설정값입니다. 구체적인 계산은 아래 사용 함수의 소스에서 확인할 수 있습니다.
UPdSaveGame.MatchPlayedCount|누적 플레이 매치 수를 저장해 다음 실행에서도 플레이 이력을 유지합니다.
UPdSaveGame.WinCount|누적 승리 수를 저장해 통계와 진행 기록을 복원합니다.
UPdSaveGame.TotalKillCount|누적 처치 수를 저장해 통계와 진행 기록을 복원합니다.
UPdSaveGame.TotalDeathCount|누적 사망 수를 저장해 통계와 진행 기록을 복원합니다.
UPdSaveGame.TotalRewardGold|누적 보상 골드를 저장해 보상 이력을 유지합니다. 현재 보유 잔액인 Gold와 구분합니다.
UPdSaveGame.ItemCollectedCount|획득 아이템 수를 저장해 수집 진행과 관련 기록을 다음 실행에 이어갑니다.
'''
EXACT = dict(line.split('|',1) for line in NOTES.strip().splitlines())

ATTRIBUTES = {'Health':'체력','Shield':'보호막','Mana':'마나','Stamina':'스태미나','Strength':'힘','Intelligence':'지능','Arcane':'비전','Armor':'방어','Recovery':'회복','Frostbite':'동상','Burn':'화상','ElectricShock':'감전','AttackSpeed':'공격 속도','MovementSpeed':'이동 속도','Critical':'치명타','FirstPandora':'첫 번째 판도라','SecondPandora':'두 번째 판도라','ThirdPandora':'세 번째 판도라','Offense':'공격','Defense':'방어','Resistance':'저항','PandoraForce':'판도라 힘','Resource':'자원','Agility':'민첩'}
INPUTS = {'Move':'이동','Look':'시점 이동','Jump':'점프','Crouch':'웅크리기','Interact':'상호작용','Attack':'공격','Aim':'조준','Grapple':'그래플','TargetConfirm':'대상 확정','OpenInfoProfile':'프로필 화면','OpenInfoItem':'아이템 화면','OpenInfoSkin':'스킨 화면','OpenInfoPandora':'판도라 화면','OpenInfoMap':'지도 화면','OpenSettingUi':'설정 화면','Escape':'취소/뒤로 가기','OpenLobby':'로비 화면','SelectPandora':'판도라 선택 화면','PandoraTree':'판도라 성장 화면','Scoreboard':'점수판','Chat':'채팅','ChatScroll':'채팅 스크롤'}


def purpose(node, field, doc, functions, selected):
    key, declaration = field['key'], field['declaration']
    if node['name']+'.'+key in EXACT:
        return EXACT[node['name']+'.'+key], 'reviewed'
    if key=='ViewModelName':
        return ('MVVM에 연결할 ViewModel의 이름 상수입니다. '+('이 이름으로 해당 ViewModel을 화면에 연결할 때 사용합니다.' if doc['uses'] else '현재 C++에서는 정의만 확인되며, 이 이름을 읽는 함수는 확인되지 않습니다.')), 'declaration'
    if node['name']=='UBasicAttributeSet':
        for suffix,tail in [('IncreasePercent','최대치 증가 비율을 계산할 때 사용하는 GAS 속성입니다.'),('Level','투자 단계를 보관해 속성 계산과 투자/회수에 사용하는 GAS 속성입니다.'),('Point','카테고리에 사용할 수 있는 포인트를 보관해 투자와 회수에 사용하는 GAS 속성입니다.')]:
            if key.endswith(suffix):
                base=key[:-len(suffix)]; maximum=base.startswith('Max');base=base.removeprefix('Max')
                return ('최대 ' if maximum else '')+ATTRIBUTES.get(base,base)+' '+tail, 'schema'
        if key in ATTRIBUTES or key.startswith('Max'):
            base=key.removeprefix('Max')
            return ('최대 ' if key.startswith('Max') else '현재 ')+ATTRIBUTES.get(base,base)+' 수치를 보관해 GAS의 효과 계산·변경·복제에 사용합니다. 생성된 Get/Set/Init 접근자와 실제 적용 함수들을 아래에 구분했습니다.', 'schema'
    if node['name']=='UControllerInputDefinition' and key.endswith('InputAction'):
        action=key.removesuffix('InputAction')
        if re.match(r'(Skill|QuickSlot|Gesture)\d$',action):
            prefix={'Skill':'스킬','QuickSlot':'퀵슬롯','Gesture':'제스처'}
            label=prefix[action[:-1]]+' '+action[-1]+'번'
        else:
            label=INPUTS.get(action,action)
        return label+' 입력에 연결할 InputAction 에셋을 지정합니다. 입력 컴포넌트가 로드·바인딩해 해당 행동의 콜백을 실행할 때 사용합니다.', 'schema'
    if doc['comment']:
        return doc['comment'], 'source-comment'
    if doc['meaning']:
        return doc['meaning'].rstrip('.')+'을(를) 보관합니다. 아래 함수들이 이 값을 조회·변경하거나 다른 처리로 전달해 해당 기능에 사용합니다.', 'reviewed-group'
    snippets='\n'.join(h['snippet'] for u in doc['uses'] for h in u['evidence'])
    if 'FTimerHandle' in declaration:
        return '예약한 '+key+' 타이머를 식별해 같은 작업의 재예약·중단·종료 정리에 사용합니다. 어떤 콜백과 연결되는지는 아래 타이머 설정/해제 함수에서 확인할 수 있습니다.', 'schema'
    if 'FDelegateHandle' in declaration:
        return '등록한 이벤트 구독을 식별해 대상 변경이나 종료 시 정확히 해제하기 위한 핸들입니다. 아래 함수에서 등록·정리 수명을 확인할 수 있습니다.', 'schema'
    if 'FStreamableHandle' in declaration:
        return '비동기 콘텐츠 로드 요청을 유지하고 요청 완료·취소·정리 시 같은 로드 작업에 접근하기 위한 핸들입니다.', 'schema'
    if 'Lease' in key:
        return '사용 중인 콘텐츠 묶음의 사용권을 유지해 필요한 동안 로드 상태를 보존하고, 사용 종료 시 반환하기 위한 데이터입니다.', 'schema'
    if key.endswith(('Generation','RequestId')):
        return '비동기 요청의 세대/식별값을 보관해 현재 요청과 이전 요청을 구분하는 데 사용합니다. 증가·비교하는 함수와 실제 조건은 아래에 표시했습니다.', 'schema'
    if '.Broadcast(' in snippets or '.AddUObject(' in snippets or '.AddDynamic(' in snippets:
        return '상태 변경을 알리거나 이벤트를 받을 구독 관계를 유지합니다. 등록·알림·해제 함수가 이 이벤트와 관련 화면/게임 처리를 연결합니다.', 'usage-pattern'
    if 'ServerValidationLogLimiter'==key:
        return '서버 검증에서 같은 실패 로그가 과도하게 반복되지 않도록 출력 제한 상태를 유지합니다.', 'schema'
    if key.startswith(('Cached','Loaded','Bound')) or key in ('OwnerHud','OwningController','ASC'):
        return '현재 연결하거나 로드한 '+key+' 대상을 유지해 이후 갱신에서 재사용하고, 대상 교체·종료 시 연결을 정리하기 위해 보관합니다.', 'schema'
    reference=next((selected[n] for n in field['references'] if n in selected and n!=node['name']),None)
    if reference:
        return reference['role']+'에 접근할 참조를 보관해 해당 데이터나 처리를 사용합니다. '+reference['purpose'], 'related-class'
    if re.search(r'U(?:Button|TextBlock|Image|Overlay|HorizontalBox|VerticalBox|TileView|ProgressBar|Slider|Widget)',declaration) or key.startswith(('Btn_','Txt_','WBP_')):
        return key+' 위젯에 접근해 화면 표시값·가시성을 갱신하거나 입력 이벤트를 연결하기 위해 참조를 유지합니다.', 'schema'
    if key.endswith(('Visibility','Opacity','Color','TextColor','Size','Padding')):
        return key+' 표시 값을 유지해 UI나 연출의 보임 여부·색상·크기·배치에 적용합니다. 표시 갱신 함수가 이 설정 또는 상태를 읽습니다.', 'schema'
    if key.endswith(('Text','TextFormat')) or 'FText ' in declaration:
        return '화면에 표시할 '+key+' 문구/형식을 보관해 상태 갱신과 안내 메시지 구성에 사용합니다.', 'schema'
    if 'Icon' in key or key.endswith('FX'):
        return key+' 시각 리소스를 보관해 해당 아이콘·효과를 생성하거나 화면에 적용할 때 사용합니다.', 'schema'
    if 'bool ' in declaration:
        return key+' 여부를 기억해 아래 함수에서 기능의 실행·표시·대기 조건을 구분합니다. 설정값인지 실행 중 상태인지는 초기화·변경 함수와 실제 선언에서 확인할 수 있습니다.', 'usage-pattern'
    if re.search(r'Seconds|Duration|Interval|Delay|LifeSpan|Time$',key):
        return key+' 시간 값을 유지해 실행 간격·대기·진행 시점 또는 종료 시점을 계산하는 데 사용합니다.', 'schema'
    if 'Settings' in key or field['schemas']:
        return key+'의 하위 설정/상태를 묶어 보관해 '+node['role']+' 처리에서 함께 읽거나 갱신합니다. 구조체 안에 저장되는 값은 아래 실제 선언에서 펼칠 수 있습니다.', 'schema'
    if 'TArray<' in declaration or 'TMap<' in declaration or 'TSet<' in declaration:
        return key+' 항목들을 한 곳에 유지해 아래 함수에서 대상 조회·순회·추가·정리에 사용합니다. 키/항목의 타입은 실제 선언과 하위 데이터에 표시했습니다.', 'schema'
    comments=[functions[u['function']]['comment'] for u in doc['uses'] if functions[u['function']]['comment'] and not functions[u['function']]['generated'] and functions[u['function']]['context']=='runtime']
    if comments:
        return key+' 값을 함수 호출 사이에 유지합니다. 관련 처리의 목적: '+comments[0], 'function-comment'
    modes={m for u in doc['uses'] for m in u['modes']}
    action='조회와 변경' if modes & {'write','update'} else '조회·전달'
    return node['role']+'에서 필요한 '+key+' 값을 유지해 아래 함수들의 '+action+'에 사용합니다. 각 사용 구문과 소스 링크에 구체적인 계산·분기·전달 위치를 기록했습니다.', 'usage-pattern'
