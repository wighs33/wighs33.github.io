"""Small connected diagrams. Repeated blocks deliberately refer to the same class."""
INTROS = {
'player':'먼저 상태의 주인과 월드의 몸체를 구분합니다. PlayerState는 전투·소유·성장 컴포넌트를, Pawn은 장비·판정·표현을 연결합니다.',
'pandora':'보유·선택 → 공통 설정 → 실제 스킬 설정 → 능력 부여 순서로 읽습니다. 판도라 성장 레벨, 설정 에셋, 발동 출처 문맥은 서로 다른 데이터입니다.',
'combat':'ASC의 상태와 Ability의 실행 책임을 나눕니다. 설정 수치를 읽는 곳, 월드에서 충돌하는 곳, 화면 표현을 만드는 곳을 따로 연결했습니다.',
'equipment':'ItemDefinition은 공유 규격이고 ItemInstance는 GUID·수량·강화 상태입니다. 인벤토리의 선택을 Equipment가 실제 무기 액터와 스탯으로 적용합니다.',
'experience':'Experience를 로드한 뒤 서버의 매치 진행·스폰·프로필 적용을 준비합니다. GameMode의 서버 책임과 GameState의 공유 상태를 구분합니다.',
'online':'비동기 온라인 요청, 로비 시작 판단, 실제 맵 이동을 분리합니다. 로비 화면은 GameState의 선택 맵·카운트다운을 읽습니다.',
'ai':'적은 자체 ASC를 가진 몸체입니다. 몬스터의 StateTree/인지 경로와 별도의 Behavior Tree 서비스·태스크 경로를 구분해 읽습니다.',
'save':'런타임 포인터를 파일에 그대로 저장하지 않습니다. 프로필은 판도라의 안정적인 에셋 ID·레벨·선택과 기록을 저장하고 입장 시 다시 적용합니다.',
'ui':'게임 상태 → 표시용 캐시/Presenter → ViewModel → 화면의 역할을 구분합니다. 점선의 화면 투영은 중간 Widget/Builder를 거치는 데이터 흐름입니다.'
}

def flow(title, explanation, names):
    return title, explanation, names.split()

FLOWS = {
'player':[
flow('01 · 플레이어 상태와 능력의 주인','몸체에서 PlayerState를 찾고, PlayerState가 만든 ASC로 능력을 실행합니다.','APdPlayer APdPlayerState UPdAbilitySystemComponent'),
flow('02 · 몸체의 공통 기능','상속과 설정 참조를 구분해서 읽습니다.','APdPlayer ACharacterBase UCharacterBaseDefinition'),
flow('03 · 플레이어 조작감 설정','현재 상태와 공유 설정을 분리합니다.','APdPlayer UPlayerPawnDefinition'),
flow('04 · 입력 정의를 액션으로','Controller → 입력 바인딩 → 매핑/액션 설정입니다.','APdPlayerController UControllerInputComponent UControllerInputDefinition'),
flow('05 · 컨트롤러 표현 설정','표현 설정의 기본 참조는 프로젝트 Definition 참조 모음에서 해석합니다.','APdPlayerController UPlayerControllerDefinition UPdGameInstanceDefinition'),
flow('06 · 이름으로 판도라 설정 찾기','이름 → 에셋 ID/경로의 색인과 실제 판도라 설정은 다릅니다.','UContentDataSubsystem UPandoraDefinition'),
flow('07 · 화면의 진입점과 라우터','HUD Actor가 라우터를 보관하고 라우터가 로컬 UI 서비스를 조회합니다.','APdHUD UHudUiRouter UUiSubsystem')],
'pandora':[
flow('01 · 무엇을 소유하고 선택했나','PlayerState의 PandoraComponent가 보유 목록과 현재 선택을 관리합니다. Instance는 정의 참조와 보유 여부만 담습니다.','APdPlayerState UPandoraComponent UPandoraInstance'),
flow('02 · 판도라 안에 실제로 무엇이 있나','판도라의 무기 조건·성장 규칙 → Skill 배열의 SkillDefinition → 비용·피해·시간·Ability 클래스까지 이어집니다.','UPandoraComponent UPandoraDefinition USkillDefinition'),
flow('03 · 설정이 실행 가능한 능력이 되는 과정','Binder가 해금된 슬롯을 읽어 SourceObject를 만들고 AbilitySpec과 함께 ASC에 부여합니다.','UPandoraComponent FPandoraSkillBinder UPandoraSkillSource'),
flow('04 · 능력은 자기 출처를 어떻게 아나','Ability는 현재 Spec의 SourceObject를 읽습니다. Source의 SkillDataAsset이 실제 스킬 설정입니다.','UPdGameplayAbility UPandoraSkillSource USkillDefinition'),
flow('05 · 출처 정보의 네트워크 수명','ASC는 Source를 복제 서브오브젝트 목록에 등록합니다. PlayerState가 Source를 직접 필드로 보관하는 관계는 아닙니다.','APdPlayerState UPdAbilitySystemComponent UPandoraSkillSource'),
flow('06 · 성장 레벨은 어디에 있나','Tree의 GrantedPandoras에는 정의와 현재 Level, PointsAvailable에는 남은 포인트가 있습니다. 정의에서는 비용·선행 조건을 읽습니다.','APdPlayerState UPandoraTreeComponent UPandoraDefinition'),
flow('07 · 세트 전환과 해금 상태 조회','선택 번호를 방향으로 해석해 판도라를 전환하고, 능력 해금은 Tree의 레벨을 조회합니다.','USelectingPandoraAndWeaponComponent UPandoraComponent UPandoraTreeComponent'),
flow('08 · 캐릭터 레벨과 스탯 투자','캐릭터 레벨/경험치는 AttributeSet의 값입니다. 판도라별 성장 레벨과 구분합니다.','ULevelingComponent UBasicAttributeSet'),
flow('09 · 스탯 투자 규칙','투자 요청 처리와 투자 상한·효과·속성 초깃값 설정을 분리합니다.','UStatUpgradeComponent UStatUpgradeDefinition')],
'combat':[
flow('01 · ASC 내부의 역할 분담','ASC가 능력 입력과 발동 대기 상태를 관리하는 객체를 보관합니다.','APdPlayerState UPdAbilitySystemComponent UAbilityGrantAndInputManager'),
flow('02 · 속성값과 적용 설정','체력·마나의 실제 값과 속성 설정의 적용 핸들은 다른 곳에 있습니다.','APdPlayerState UBasicAttributeSet'),
flow('03 · 속성 설정 관리자','ASC의 AttributeManager가 설정 적용/해제 수명을 관리합니다.','UPdAbilitySystemComponent UAbilityAttributeManager'),
flow('04 · 비용과 시간 설정 사용','능력 실행기가 SkillDefinition의 마나와 쿨다운/지속 시간을 조회합니다.','UPdGameplayAbility UAbilityCostAndCooldownManager USkillDefinition'),
flow('05 · 능력 연출 관리자','활성 연출 액터와 자기 버프 표현 대상을 추적합니다.','UPdGameplayAbility UAbilityPresentationManager'),
flow('06 · 일반 공격 실행','AttackAbility는 공통 Ability를 상속하고 CombatComponent로 공격 구간을 처리합니다.','UAttackAbility UCombatComponent AWeaponBase'),
flow('07 · 투사체 준비와 충돌','Ability의 준비된 투사체가 피해 Spec과 상태이상 설정을 가지고 월드를 이동합니다.','UProjectileAbility AProjectileBase UStatusEffectDefinition'),
flow('08 · 투사체 능력의 공통 동작','공통 비용·출처·연출 로직을 재사용합니다.','UProjectileAbility UPdGameplayAbility'),
flow('09 · 사망과 상태이상 표시','공통 몸체가 사망 처리 컴포넌트를 보관합니다.','ACharacterBase UCharacterDeathComponent'),
flow('10 · 복제할 상태이상 목록','스택을 복제하는 컴포넌트와 스택 목록의 수명을 구분합니다.','ACharacterBase UStatusEffectReplicationComponent')],
'equipment':[
flow('01 · 공통 규격과 개별 아이템','소유 목록 → GUID/수량/강화 → 공통 스탯·소모 효과·무기 설정입니다.','UInventoryComponent UItemInstance UItemDefinition'),
flow('02 · 선택을 실제 무기로','장비 컴포넌트는 현재 무기 액터를 추적하고 액터는 아이템 정의를 사용합니다.','UEquipmentComponent AWeaponBase UItemDefinition'),
flow('03 · 검의 공통 동작','추가 필드가 없는 검 타입은 부모의 판정/표현 상태를 사용합니다.','ASword AWeaponBase'),
flow('04 · 총과 활의 차이','총은 다음 발사 시각을 추가로 저장합니다.','AGun AWeaponBase'),
flow('05 · 활의 준비 상태','활은 준비된 화살과 서버 시위 당김 상태를 추가로 관리합니다.','ABow AWeaponBase'),
flow('06 · 처치 보상','지급 요청의 대기 상태와 보상 수치·정책 에셋을 분리합니다.','APdPlayerState UPlayerRewardComponent URewardDefinition'),
flow('07 · 시작 콘텐츠 지급','지급 절차가 모드별 에셋 목록과 수치를 읽습니다.','UDefaultPlayerProvisioner UDefaultProvisionDefinition'),
flow('08 · 무기와 판도라 세트 전환','선택한 방향에서 인벤토리의 무기를 찾고 장비 교체를 요청합니다.','USelectingPandoraAndWeaponComponent UEquipmentComponent UInventoryComponent')],
'experience':[
flow('01 · 공유할 Experience 선택','GameState에 있는 Manager가 에셋 ID를 로드 상태로 해석합니다.','AExperienceGameState UExperienceManagerComponent UExperienceDefinition'),
flow('02 · 서버의 매치 진행','서버 GameMode가 진행 컴포넌트와 규칙 에셋을 연결합니다.','AExperienceGameMode UExperienceMatchFlowComponent'),
flow('03 · 서버의 스폰 책임','Controller별 시작 지점과 초기 위치를 관리합니다.','AExperienceGameMode UExperienceSpawnComponent'),
flow('04 · 플레이어 입장 준비','프로필 적용과 기본 지급을 준비 완료 상태와 함께 조정합니다.','AExperienceGameMode UExperiencePlayerProvisioningComponent UExperiencePlayerProfileService'),
flow('05 · 시간·승패·리스폰 정책','규칙은 에셋에, 진행 상태는 컴포넌트/GameState에 있습니다.','AExperienceGameMode UMatchRuleDefinition'),
flow('06 · 플레이어 식별 정보','팀/스폰 슬롯·닉네임과 현재 매치 사망 수를 PlayerState의 컴포넌트에서 읽습니다.','APdPlayerState UPlayerMatchComponent'),
flow('07 · 게임 맵 선택','기본 맵 설정은 프로젝트 Definition 참조를 통해 찾습니다.','AExperienceGameMode ULevelDefinition'),
flow('08 · Game Feature 구성 순서','헤더에 명시된 구성 지침: 능력 부여 뒤 Actor 확장. 직접 멤버 참조나 모든 에셋의 실제 실행 순서를 뜻하지 않습니다.','UGameFeatureAction_AddAbilities UGameFeatureAction_AddActorExtension'),
flow('09 · 프로젝트 능력 설정 검사','능력 부여 액션은 PdGameplayAbility의 기본 객체를 검사해 설정 유효성을 확인합니다.','UGameFeatureAction_AddAbilities UPdGameplayAbility')],
'online':[
flow('01 · 세션 종료 요청','Controller의 종료 경로가 온라인 세션 서비스에 작업을 요청합니다.','APdPlayerController UControllerSessionComponent UOnlineSessionsSubsystem'),
flow('02 · 시작 판단과 실제 이동','로비 GameMode는 카운트다운 담당과 이동 담당을 별도로 둡니다.','ALobbyGameMode ULobbyMatchCoordinator'),
flow('03 · 온라인 세션 시작 후 이동','TravelCoordinator가 준비한 URL과 세션 시작 콜백 수명을 관리합니다.','ALobbyGameMode ULobbyTravelCoordinator UOnlineSessionsSubsystem'),
flow('04 · 로비 구성 로드','맵·규칙·초기 지급 에셋을 로드한 뒤 유효한 로비 옵션을 만듭니다.','ALobbyGameMode ULobbyConfigurationComponent ULevelDefinition'),
flow('05 · 맵 이동에 필요한 캐시','런타임 로비 캐시는 맵 설정과 플레이어 이동 정보를 제공합니다.','ULobbyRuntimeSubsystem ULevelDefinition'),
flow('06 · 로비 UI의 데이터 원본','화면은 GameState의 선택 맵과 서버 기준 시작 시각을 조회합니다.','ULobbyWidget ALobbyGameState UExperienceManagerComponent'),
flow('07 · 로비 플레이어 보조 상태','로비 이탈/닉네임 힌트와 정식 매치 식별 정보는 구분됩니다.','APdPlayerState ULobbyPlayerStateComponent')],
'ai':[
flow('01 · 적의 설정과 능력 시스템','적은 자신의 ASC를 가지고 공통 전투 설정을 로드합니다.','AEnemyBase UEnemyBaseDefinition'),
flow('02 · 플레이어와 다른 ASC 소유 위치','플레이어 ASC는 PlayerState에, 적 ASC는 EnemyBase에 있습니다.','AEnemyBase UPdAbilitySystemComponent'),
flow('03 · 몬스터 몸체와 공격','몬스터는 적 몸체를 상속합니다. 적의 공격 대상/타이머는 별도 컴포넌트가 관리합니다.','AMonsterCharacter AEnemyBase UEnemyCombatComponent'),
flow('04 · 몬스터 StateTree 경로','AIController가 적 설정의 StateTree를 읽어 인지/행동을 시작합니다.','AMonsterAIController UEnemyBaseDefinition'),
flow('05 · 훈련 봇 동작','피격 경직·장비 교체·복구 위치는 훈련 컴포넌트가 관리합니다.','AEnemyBase UEnemyTrainingBotComponent UItemDefinition'),
flow('06 · 별도 Behavior Tree 경로','BT 서비스는 EnemyBase를 조회해 블랙보드의 대상 정보를 갱신합니다.','UBTService_UpdateEnemyTarget AEnemyBase'),
flow('07 · BT의 공격 요청','BT 태스크가 거리/이동 정책에 따라 EnemyBase의 공격 동작을 요청합니다.','UBTTask_EnemyAttack AEnemyBase')],
'save':[
flow('01 · 메모리 프로필과 저장 파일','프로필 서비스가 플레이어 ID별 SaveGame을 캐시합니다.','UPlayerProfileSubsystem UPdSaveGame'),
flow('02 · 파일 포장과 복원','Envelope가 직렬화 바이트를 검증·복원해 SaveGame 객체를 만듭니다.','UProfileSaveEnvelope UPdSaveGame'),
flow('03 · 저장 예약에서 파일 포장까지','저장 서비스가 변경된 프로필의 Envelope를 생성해 저장합니다.','UPlayerProfileSubsystem UProfileSaveEnvelope'),
flow('04 · 입장할 때 프로필 적용','매치 입장 서비스가 로컬 프로필 서비스와 PlayerState를 연결합니다.','UExperiencePlayerProfileService UPlayerProfileSubsystem'),
flow('05 · 외형 프로필 동기화','Controller 컴포넌트가 로컬 프로필에서 외형 정보를 읽고 동기화를 요청합니다.','APdPlayerController UControllerProfileSyncComponent UPlayerProfileSubsystem')],
'ui':[
flow('01 · HUD와 화면 서비스','라우터가 로컬 플레이어의 UI 서비스를 조회합니다. 화면 클래스 설정은 공통 에셋에서 읽습니다.','UHudUiRouter UUiSubsystem UWidgetClassDefinition'),
flow('02 · 플레이 중 HUD 설정','HUD Widget은 전달받은 화면 클래스 정의를 사용합니다.','UPlayerHudWidget UWidgetClassDefinition'),
flow('03 · 정보 화면의 상태 연결','Presenter가 로드아웃 캐시를 보관하고 캐시는 원본 판도라 상태를 구독합니다.','UInfoUiPresenter UInfoLoadoutStore UPandoraComponent'),
flow('04 · 판도라 탭 선택과 필터','탭 Presenter는 선택 슬롯/필터를 적용해 로드아웃 데이터를 표현합니다.','UInfoUiPresenter UInfoPandoraTabPresenter UInfoLoadoutStore'),
flow('05 · 판도라 카드로 투영','PandoraWidget/Builder를 거쳐 정의와 성장 상태를 카드 이름·레벨·잠금 상태로 바꿉니다.','UPandoraDefinition UPandoraWidgetViewModel'),
flow('06 · 판도라 설명으로 투영','PandoraDescriptionWidget/Builder가 SkillDefinition의 이름·설명·아이콘까지 읽어 상세 표시값을 만듭니다.','UPandoraDefinition UPandoraDescriptionViewModel'),
flow('07 · 성장 포인트로 투영','PandoraTreeWidget을 거쳐 남은 포인트를 ViewModel에 전달합니다.','UPandoraTreeComponent UPandoraTreeViewModel'),
flow('08 · 체력은 원본 속성을 구독','ViewModel이 ASC의 AttributeSet 값 변경을 구독해 화면 수치와 비율을 만듭니다.','UHealthBarViewModel UBasicAttributeSet'),
flow('09 · 스킬 바와 개별 쿨다운','스킬 바가 개별 슬롯을 생성·초기화하고 슬롯은 능력 핸들에 연결됩니다.','UAbilitiesBarWidget UAbilitySlotWidget'),
flow('11 · 설정과 표시값을 연결하는 실제 Widget','Widget은 판도라 정의와 Tree를 함께 읽고 DescriptionViewModel을 생성/갱신합니다.','UPandoraDescriptionWidget UPandoraDescriptionViewModel'),
flow('12 · 설명할 판도라와 스킬 설정','Widget의 Definition에서 Skill 배열을 따라 실제 스킬 설정을 읽습니다.','UPandoraDescriptionWidget UPandoraDefinition USkillDefinition'),
flow('10 · 상점 데이터','상점은 카탈로그의 상품 참조와 자동 포함 정책으로 목록을 만듭니다.','UShopWidget UShopCatalogDefinition')]
}

# source>target | kind | short label | payload | precise meaning | evidence filename | exact source substring
RELATIONSHIPS = r'''
UHudUiRouter>UUiSubsystem|runtime|화면 서비스 조회|LocalPlayer Subsystem|라우터가 로컬 플레이어의 UiSubsystem을 조회해 화면/모달 입력 서비스를 사용합니다. OwnerHud 필드는 APdHUD의 약한 참조입니다.|HudUiRouter.cpp|GetSubsystem<UUiSubsystem>()
APdPlayer>APdPlayerState|runtime|상태 조회|GetPlayerState|플레이어 몸체는 자신의 PlayerState에서 ASC와 플레이어 상태를 얻습니다.|PdPlayer.cpp|GetPlayerState<APdPlayerState>
APdPlayerState>UPandoraComponent|ownership|생성·소유|CreateDefaultSubobject|PlayerState 생성자에서 PandoraComponent를 생성합니다. 실제 보유·선택 데이터는 이 컴포넌트에 있습니다.|PdPlayerState.cpp|PandoraComponent = CreateDefaultSubobject
APdPlayerState>UPandoraTreeComponent|ownership|생성·소유|성장 목록·포인트|PlayerState가 Tree를 생성합니다. 판도라별 Level과 남은 포인트가 이곳에 있으며 Source나 Instance의 값과 다릅니다.|PdPlayerState.cpp|PandoraTreeComponent = CreateDefaultSubobject
APdPlayerState>UPdAbilitySystemComponent|ownership|생성·소유|능력·효과 실행기|PlayerState 생성자에서 ASC를 만들며 판도라 Source 복제는 ASC가 담당합니다.|PdPlayerState.cpp|AbilitySystemComponent = CreateDefaultSubobject
UPlayerControllerDefinition>UPdGameInstanceDefinition|config|기본 설정 조회|프로젝트 Definition 참조|컨트롤러 표현 Definition의 기본 에셋을 프로젝트 공통 참조 모음에서 해석합니다.|PlayerControllerDefinition.cpp|GetConfiguredDefinitionReferences()
UContentDataSubsystem>UPandoraDefinition|runtime|에셋 해석·조회|이름 → PrimaryAssetId → 정의|판도라 이름을 에셋 ID로 해석하고 로드된 Definition을 조회합니다. 아이콘·무기 조건·스킬 수치는 반환된 에셋에 있습니다.|ContentDataSubsystem.cpp|UPandoraDefinition* UContentDataSubsystem::
UPandoraComponent>FPandoraSkillBinder|runtime|능력 부여 요청|정의·성장 레벨·방향|컴포넌트가 Binder에 판도라 정의와 레벨·방향을 전달하고 반환된 능력 핸들을 보관합니다.|PandoraComponent.cpp|FPandoraSkillBinder::GrantPandoraContent(
FPandoraSkillBinder>UPandoraSkillSource|ownership|출처 객체 생성|ASC를 Outer로 생성|Binder가 ASC를 Outer로 Source를 만들고 정의·스킬 에셋·인덱스·슬롯 요구 레벨·방향을 초기화합니다. Source를 AbilitySpec.SourceObject로 연결해 GiveAbility합니다.|PandoraSkillBinder.cpp|NewObject<UPandoraSkillSource>(ASC)
FPandoraSkillBinder>UPdAbilitySystemComponent|runtime|서버에서 능력 부여|FGameplayAbilitySpec + SourceObject|해금된 슬롯의 Ability 클래스로 Spec을 만들고 SourceObject에 SkillSource를 붙여 ASC에 부여합니다. 반환 핸들을 컴포넌트가 추적합니다.|PandoraSkillBinder.cpp|ASC->GiveAbility(Spec)
UPdAbilitySystemComponent>UPandoraSkillSource|ownership|보관·복제 등록|GrantedPandoraSkillSources|ASC가 Source를 추적하고 권한이 있는 준비된 인스턴스에서 복제 서브오브젝트로 등록합니다.|PdAbilitySystemComponent.cpp|AddReplicatedSubObject(SkillSource)
UPdGameplayAbility>UPandoraSkillSource|runtime|발동 출처 조회|Spec.SourceObject|GetCurrentSourceObject를 SkillSource로 해석해 판도라·스킬 인덱스·레벨·방향을 얻습니다. 방향별 피해 보정과 출처별 쿨다운 식별에 사용합니다.|PdGameplayAbility.cpp|return Cast<UPandoraSkillSource>(GetCurrentSourceObject())
UPandoraComponent>UPandoraTreeComponent|runtime|성장 레벨 조회|GrantedPandoras의 Level|PlayerState의 Tree를 찾아 해당 판도라의 현재 성장 레벨을 읽습니다. 능력 슬롯 해금과 갱신의 기준입니다.|PandoraComponent.cpp|PlayerStateOwner->GetPandoraTreeComponent()
USelectingPandoraAndWeaponComponent>UPandoraComponent|runtime|선택 전환 요청|선택 번호 → 방향·판도라|서버가 선택 번호를 방향으로 바꿔 해당 슬롯의 Definition을 조회하고 판도라 선택 변경을 요청합니다.|SelectingPandoraAndWeaponComponent.cpp|PandoraComponent->RequestPandoraSelectionForDirection
USelectingPandoraAndWeaponComponent>UEquipmentComponent|runtime|장착 전환 요청|방향 + ItemInstance|선택한 방향에서 인벤토리의 무기를 찾고 Equipment에 장착을 요청합니다. 빈 슬롯이면 해제를 요청합니다.|SelectingPandoraAndWeaponComponent.cpp|Equipment->RequestWeaponSelectionForDirection
ULevelingComponent>UBasicAttributeSet|runtime|속성 조회·변경|레벨·경험치·포인트|컴포넌트는 AttributeSet의 레벨/경험치 값을 조회하고 효과/태그로 성장 처리를 연결합니다.|LevelingComponent.cpp|UBasicAttributeSet
UAbilityCostAndCooldownManager>USkillDefinition|runtime|비용·시간 조회|ManaCost / Time|능력의 출처 스킬 설정을 읽어 마나 비용과 쿨다운 시간을 처리합니다. 현재 남은 쿨다운은 설정 에셋에 저장하지 않습니다.|AbilityCostAndCooldownManager.cpp|GetSourceSkillDataAsset()
UAttackAbility>UCombatComponent|runtime|공격 구간 실행|콤보·판정 창|Ability가 몸체의 CombatComponent를 조회해 공격 구간과 타격 처리를 연결합니다.|AttackAbility.cpp|UCombatComponent
UCombatComponent>AWeaponBase|runtime|현재 무기 조회|무기 판정·피해 문맥|CombatComponent가 현재 무기를 조회해 무기 공격 판정과 피해 설정을 사용합니다.|CombatComponent.cpp|AWeaponBase
AExperienceGameMode>ULevelDefinition|config|기본 맵 설정 조회|프로젝트 LevelDefinition|GameMode가 프로젝트 Definition 참조 모음의 맵 설정을 사용합니다.|ExperienceGameMode.cpp|GetConfiguredDefinitionReferences().LevelDefinition
UGameFeatureAction_AddAbilities>UGameFeatureAction_AddActorExtension|sequence|구성 순서 지침|능력 부여 뒤 확장|프로젝트 헤더는 능력 부여 뒤 Actor 확장을 배치하도록 명시합니다. 직접 포인터/호출 관계가 아니라 기능 액션의 구성 순서 지침입니다.|GameFeatureAction_AddAbilities.h|5. Add Actor Extension
UGameFeatureAction_AddAbilities>UPdGameplayAbility|runtime|기본 객체 검사|능력 설정 검증|부여할 능력 클래스의 기본 객체를 PdGameplayAbility로 해석해 프로젝트 능력 설정을 검증합니다.|GameFeatureAction_AddAbilities.cpp|Cast<UPdGameplayAbility>(AbilityClass->GetDefaultObject())
UControllerSessionComponent>UOnlineSessionsSubsystem|runtime|세션 서비스 요청|방 나가기·세션 정리|Controller의 세션 컴포넌트가 게임 인스턴스의 온라인 세션 서비스를 조회합니다.|ControllerSessionComponent.cpp|GetSubsystem<UOnlineSessionsSubsystem>
ULobbyTravelCoordinator>UOnlineSessionsSubsystem|runtime|세션 시작 요청|비동기 시작 완료|이동 담당자가 온라인 세션 서비스의 시작 결과를 기다리고 맵 이동을 진행합니다.|LobbyTravelCoordinator.cpp|GetSubsystem<UOnlineSessionsSubsystem>
ULobbyWidget>ALobbyGameState|runtime|공유 상태 조회|선택 맵·시작 시각|로비 Widget이 월드의 LobbyGameState를 조회해 선택 맵과 카운트다운을 표시합니다.|LobbyWidget.cpp|GetGameState<ALobbyGameState>()
AMonsterAIController>UEnemyBaseDefinition|config|StateTree 설정 조회|MonsterStateTree|몬스터 AIController가 EnemyBaseDefinition을 조회해 실행할 StateTree 설정을 읽습니다. 아래 BT 클래스와 직접 이어지는 실행 경로는 아닙니다.|MonsterAIController.cpp|UEnemyBaseDefinition
UBTService_UpdateEnemyTarget>AEnemyBase|runtime|대상 상태 조회|블랙보드 대상·거리|BT 서비스가 Controller의 Pawn을 EnemyBase로 해석해 대상·거리·사거리·시야 키를 갱신합니다.|BTService_UpdateEnemyTarget.cpp|Cast<AEnemyBase>
UBTTask_EnemyAttack>AEnemyBase|runtime|공격 행동 요청|사거리·접근 정책|BT 태스크가 Controller의 EnemyBase를 얻고 사거리·이동 정책에 맞춰 공격을 요청합니다.|BTTask_EnemyAttack.cpp|Cast<AEnemyBase>
UProfileSaveEnvelope>UPdSaveGame|runtime|바이트를 프로필로 복원|ID·리비전·CRC 검증|Envelope는 난독화된 바이트를 복원하고 SaveGame 타입/식별 정보를 확인합니다. 클래스 포인터를 디스크에 저장하는 의미가 아닙니다.|PdSaveGame.cpp|UPdSaveGame* UProfileSaveEnvelope::DecodeProfile
UPlayerProfileSubsystem>UProfileSaveEnvelope|runtime|저장 컨테이너 생성|직렬화할 프로필 스냅샷|프로필 저장 서비스가 Envelope를 생성해 식별자·리비전과 프로필 바이트를 묶습니다.|PlayerProfileSubsystemStorage.cpp|UProfileSaveEnvelope::CreateFromProfile(
UExperiencePlayerProfileService>UPlayerProfileSubsystem|runtime|입장 프로필 조회|플레이어 프로필 적용|매치 입장 서비스가 GameInstance의 프로필 서비스를 조회하고 플레이어 초기 상태 적용을 연결합니다.|ExperiencePlayerProfileService.cpp|GetSubsystem<UPlayerProfileSubsystem>
UControllerProfileSyncComponent>UPlayerProfileSubsystem|runtime|로컬 외형 조회|프로필 스킨 정보|Controller의 동기화 컴포넌트가 프로필 서비스를 조회해 외형 데이터 동기화를 준비합니다.|ControllerProfileSyncComponent.cpp|GetSubsystem<UPlayerProfileSubsystem>
UPandoraDefinition>UPandoraWidgetViewModel|projection|카드 표시로 투영|PandoraWidget / Builder 경유|중간 Widget/Builder가 판도라 정의와 성장 상태를 읽고 이름·아이콘·레벨·잠금 표시값을 ViewModel에 적용합니다. Definition이 ViewModel을 직접 소유하지 않습니다.|PandoraWidget.cpp|UPandoraWidgetViewModel* ViewModel
UPandoraDefinition>UPandoraDescriptionViewModel|projection|설명 표시로 투영|DescriptionWidget / Builder 경유|Widget이 정의와 Tree로 설명 데이터를 만들고 제목·무기 조건·단계별 비용·스킬별 이름/설명/아이콘을 ViewModel에 전달합니다.|PandoraDescriptionWidget.cpp|FPandoraDescriptionViewDataBuilder::Build(
UPandoraTreeComponent>UPandoraTreeViewModel|projection|포인트를 화면에 전달|PandoraTreeWidget 경유|TreeWidget이 컴포넌트의 남은 포인트를 읽어 ViewModel의 숫자와 표시 텍스트를 갱신합니다.|PandoraTreeWidget.cpp|ViewModel->SetPointsAvailable(PointsAvailable)
UHealthBarViewModel>UBasicAttributeSet|runtime|속성 변경 구독|체력·최대 체력·경험치|ViewModel이 ASC의 AttributeSet 값 변경 델리게이트를 구독하고 체력/경험치 화면 값을 갱신합니다.|HealthBarViewModel.cpp|GetGameplayAttributeValueChangeDelegate(UBasicAttributeSet::GetHealthAttribute())
UAbilitiesBarWidget>UAbilitySlotWidget|runtime|슬롯 생성·초기화|AbilitySpecHandle·스킬 인덱스|스킬 바가 생성한 Widget을 AbilitySlotWidget으로 해석해 능력 핸들과 슬롯별 표시 정보를 연결합니다.|AbilitiesBarWidget.cpp|UAbilitySlotWidget
'''

def relationships():
    result = {}
    for line in RELATIONSHIPS.splitlines():
        if line.strip():
            key,kind,label,payload,detail,file,needle = line.split('|')
            assert key not in result
            result[key] = dict(kind=kind,label=label,payload=payload,detail=detail,file=file,needle=needle)
    return result
