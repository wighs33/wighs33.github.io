"""Editorial layer for the 100-class atlas. Field identifiers are checked against C++."""

# name | role | storage | purpose | field names : meaning (semicolon separated)
NOTES = r'''
APdHUD|게임 화면의 진입점|HUD Actor / 로컬 UI|라우터를 통해 메뉴·화면·스코어보드를 연결하고 화면 위젯과 Presenter를 캐시합니다.|UiRouter:화면 계층과 모달 입력을 연결하는 라우터;WidgetClassDefinition:사용할 위젯 클래스 설정;CachedPlayerHUD,CachedInfoUiPresenter:생성한 플레이 HUD와 정보 화면 Presenter 캐시
UPandoraDescriptionWidget|판도라 정의와 설명 화면 연결|로컬 UI Widget|판도라 설정과 성장 상태를 Builder에 전달하고 그 결과를 설명 ViewModel에 적용합니다. 설정의 스킬 이름·설명·아이콘이 화면 데이터가 되는 연결 지점입니다.|PandoraDefinition:설명할 판도라와 슬롯별 스킬 설정;PandoraTreeComponent:현재 판도라 성장 레벨과 남은 포인트;PandoraDescriptionViewModel:화면에 적용할 제목·무기 조건·스킬 설명 표시값
APdPlayerState|플레이어 상태의 중심|플레이어 런타임|플레이어의 능력·소유 목록·성장 컴포넌트를 묶습니다. 체력 수치나 스킬 설정을 이 클래스의 필드에 직접 중복 저장하지 않습니다.|AbilitySystemComponent,BasicAttributeSet:능력 실행기와 실제 체력·마나·레벨 수치;PandoraComponent,PandoraTreeComponent:소유·선택한 판도라와 판도라별 성장/포인트;InventoryComponent,SelectingPandoraAndWeaponComponent:소유 아이템과 현재 무기·판도라 세트 선택;PlayerMatchComponent,LobbyPlayerStateComponent:매치 식별 정보와 로비 이탈 상태
APdPlayer|조작하는 플레이어 캐릭터|Pawn 런타임|월드에서 이동하고 싸우는 플레이어 몸체입니다. 플레이어 전투 상태의 ASC는 PlayerState와 연결하고 몸체의 입력·카메라·전투 설정은 별도 에셋으로 읽습니다.|PlayerPawnDefinition:상호작용·카메라·조준·전투 설정 에셋;CombatComponent:공격 판정과 콤보 실행 컴포넌트
ACharacterBase|캐릭터 공통 몸체|Actor 런타임|플레이어와 적이 공유하는 장비·죽음·상태이상·표현 기능을 모읍니다. 파생 캐릭터가 능력 시스템과 구체적인 설정을 연결합니다.|CharacterDefinition,LoadedCharacterDefinition:공통 표현·죽음 설정의 소프트 참조와 로드 결과;EquipmentComponent,CharacterDeathComponent:장비 실행과 사망/복구 담당;StatusEffectReplicationComponent:상태이상 스택의 복제 담당;FactionId:진영 식별값
APdPlayerController|입력과 로컬 서비스 연결|Controller 런타임|입력, 온라인 세션, 프로필 동기화와 화면 표현을 컴포넌트에 분배합니다.|PlayerControllerDefinition:컨트롤러 표현 설정;ControllerInputComponent:입력 매핑과 액션 바인딩;ControllerSessionComponent,ControllerProfileSyncComponent:세션 종료와 프로필 동기화 경로
UContentDataSubsystem|콘텐츠 이름·에셋 색인|게임 인스턴스 캐시|판도라·스킬·스킨의 이름을 에셋 ID/경로로 해석하고 비동기 로드를 준비합니다. 실제 스킬 수치의 원본은 Definition 에셋입니다.|SkillDataAssetIdsByName,PandoraDefinitionIdsByName:콘텐츠 이름 → 안정적인 Primary Asset ID 색인;SkillDataAssetPathsByName,PandoraDefinitionPathsByName:이름 → 에셋 소프트 경로 캐시
UPlayerPawnDefinition|플레이어 몸체 설정|설정 Data Asset|플레이어 조작감과 기본 전투 정책을 묶은 설정입니다. 현재 조준 대상이나 공격 진행 상태를 저장하는 곳은 아닙니다.|Interaction,Camera,Aim:상호작용·카메라·조준 설정 묶음;ActionPolicy:행동 허용/제한 정책;UnarmedCombatSettings,CombatDamageSettings:맨손 판정과 피해 계산 설정
UCharacterBaseDefinition|공통 캐릭터 설정|설정 Data Asset|캐릭터의 공통 표현과 사망 처리를 에셋으로 분리합니다.|Presentation:공통 캐릭터 표현 설정;Death:사망·디졸브·복구 설정
UPlayerControllerDefinition|컨트롤러 표현 설정|설정 Data Asset|컨트롤러에 적용할 화면 표현 설정을 제공합니다.|Presentation:컨트롤러 표현 설정 구조체
UPdGameInstanceDefinition|프로젝트 설정 참조 모음|설정 Data Asset|프로젝트에서 사용할 여러 Definition 에셋을 한 곳에서 연결합니다.|Memo:설정 에셋을 설명하는 편집용 메모;Definitions:프로젝트 공통 Definition 참조 묶음
UControllerInputComponent|입력을 행동으로 전달|Controller 런타임|입력 정의를 로드하고 액션을 바인딩합니다. 입력 매핑 적용 결과와 바인딩 수명을 관리합니다.|ActiveInputDefinition,LoadedInputDefinition:선택한 입력 설정과 로드된 에셋;AppliedInputMapping:현재 적용한 Enhanced Input 매핑;LoadedInputActions,BindingHandles:로드된 액션과 해제에 사용할 바인딩 핸들
UControllerInputDefinition|키·액션 매핑 설정|설정 Data Asset|이동·공격·스킬·퀵슬롯·화면 조작을 어떤 입력 액션으로 받을지 정의합니다.|InputMapping,Priority:적용할 매핑 컨텍스트와 우선순위;MoveInputAction,LookInputAction,JumpInputAction:이동·시점·점프 액션;CharacterActionDefinition,InputActionIconMappings:행동 설정 참조와 입력 아이콘 대응표

UPandoraComponent|소유 판도라와 장착 슬롯|PlayerState 컴포넌트|정의 기반 보유 목록·현재 선택·방향별 로드아웃·부여 능력 핸들을 관리합니다. 성장 레벨과 남은 포인트는 Tree에서 읽습니다.|AllPandoraList,ReplicatedEntries:표시 목록은 Definition 참조, 복제 항목은 Definition + IsOwned;CurrentPandoraDefinition,CurrentPandoraLoadoutDirection:현재 선택과 방향;PandoraLoadoutSlots:방향별 PandoraDefinition;GrantedPandoraAbilityHandles:부여된 판도라 스킬 핸들
UPandoraDefinition|판도라가 무엇인지 정의|설정 Data Asset|표시 정보·무기 조건·성장 비용·선행 조건과 Skills 배열을 담습니다. 슬롯은 USkillDefinition을 직접 참조하며 외부에서는 Getter로 읽습니다.|DisplayName,Description,IconTexture,IdTag:표시 정보와 식별 태그;ActivatableWeaponTags:호환 무기 태그;MaxLevel,PointsRequiredPerLevel:고정 최대 레벨과 단계별 비용;UnlockRules:선행 판도라와 요구 레벨;Skills:슬롯 순서대로 USkillDefinition 직접 참조;Tier,ShopData:티어와 상점 설정
UPandoraSkillSource|판도라 스킬의 출처 식별|ASC 복제 서브오브젝트|AbilitySpec.SourceObject에 연결됩니다. 정의와 슬롯 인덱스로 스킬을 조회하고, 이 SourceObject가 붙은 ASC의 활성 쿨다운 효과를 조회합니다.|PandoraDefinition:출처 판도라 정의;SkillIndex:Skills 배열에서 조회할 슬롯 인덱스;PandoraLevel:Binder가 전달한 슬롯 요구 레벨;LoadoutDirection:시전의 로드아웃 방향
FPandoraSkillBinder|판도라 설정을 능력으로 부여|상태 없는 C++ 처리|서버에서 해금된 슬롯마다 공통 USkillAbility의 Spec과 SkillSource를 만들어 ASC에 부여합니다. 기존 능력을 재사용하고 입력 태그를 갱신하며, 멤버 저장 필드는 없습니다.|
UPandoraTreeComponent|판도라별 성장과 포인트|PlayerState 컴포넌트|어떤 판도라를 몇 단계까지 성장시켰는지와 남은 포인트를 관리합니다. Definition의 비용·선행 조건을 검사한 뒤 성장 상태를 갱신합니다.|GrantedPandoras:각 항목에 PandoraDefinition 참조와 현재 Level 저장;PointsAvailable:현재 사용할 수 있는 판도라 포인트;InitialGrantedPandoras,InitialPointsAvailable:초기 부여 목록과 시작 포인트 설정
USkillDefinition|스킬 설정과 액션 트리|설정 Data Asset|비용·시간·피해·상태 이상·연출과 실행할 Action 템플릿을 보관합니다. 모든 판도라 스킬은 USkillAbility가 이 트리를 복제해 실행합니다.|SkillType:Instant·Press·Duration 종료 정책;Activation:입력·태그·사용 횟수 정책;Action:에셋에 저장되는 Instanced 액션 템플릿;Name,Description,Icon:화면 표시 정보;ManaCost,Time:마나 비용·쿨다운·전체 지속시간;Damage,StatusEffectDataAsset,StackCount:피해 Spec 설정과 적중 시 누적 상태 이상
USelectingPandoraAndWeaponComponent|무기·판도라 세트 선택|PlayerState 컴포넌트|선택 번호를 기준으로 무기와 판도라의 로드아웃 방향을 함께 전환합니다. 요청을 서버에서 적용합니다.|SelectedPandoraAndWeaponNumber:현재 선택한 무기·판도라 세트 번호
ULevelingComponent|경험치와 레벨 상승 처리|PlayerState 컴포넌트|레벨 상승용 효과와 스탯 태그를 이용해 수치를 변경합니다. 실제 레벨·경험치 값은 BasicAttributeSet에 있습니다.|LevelingGameplayEffectClass:레벨 변경을 적용할 GameplayEffect;LevelStatTag,ExperienceStatTag:변경할 레벨·경험치 속성 태그;CategoryPointStatTags,PointsPerCategoryOnLevelUp:레벨 상승 시 지급할 카테고리 포인트 태그와 수량
UStatUpgradeComponent|스탯 초기화와 투자 요청|PlayerState 컴포넌트|정의를 로드하고 서버 속성 초기화 시점과 중복 적용을 관리합니다. 투자·환불 계산 결과의 실제 적용은 ASC에 요청합니다.|StatUpgradeDefinition,LoadedStatUpgradeDefinition:스탯 정의 소프트 참조와 로드 결과;bApplyingStatChange:중복/재진입 변경 방지
UStatUpgradeDefinition|스탯 규칙과 초기값 계산|설정 Data Asset|기본값과 시작 투자분을 같은 투자 공식으로 계산합니다. 최대 자원을 먼저 적용할 순서와 채울 현재 자원 목록을 ASC에 전달합니다.|AttributeDefaultValues:태그·기본값·투자당 값·우선순위;UpgradeRules:분류별 비용·투자 규칙;PairedResourceStatTags:최대/현재 자원 연결;MaxInvestedLevel:허용 투자 상한

UPdAbilitySystemComponent|능력·효과 실행과 속성 적용|플레이어/적 런타임|속성 초기화·변경·리셋을 직접 수행하고 입력은 관리자에 위임합니다. 출처 복제 지연 시 활성화를 보류하고, 종료·취소 시 대기 상태를 정리합니다.|GrantedPandoraSkillSources:출처 객체 보관·복제 등록;ActivationsWaitingForSource:출처 복제를 기다리는 서버 활성화 통지;AbilityGrantAndInputManager:입력 전달과 능력 부여 관리자
UPdGameplayAbility|게임 능력 공통 실행|Ability 인스턴스|AbilitySpec의 출처로부터 SkillSource와 SkillDefinition을 얻어 비용·쿨다운·이동·연출에 사용합니다.|CostAndCooldownManager,PresentationManager:비용/쿨다운과 화면 연출 실행 관리자;ActiveSelfBuffEffectHandle:이 능력이 적용한 자기 버프 효과 핸들
UBasicAttributeSet|전투 수치와 보정 계산|GAS 속성 / 복제|실제 자원·성장 수치를 보관하며 신비에 따른 쿨다운, 상태 이상 피해 보정과 Spec의 피해 기록을 처리합니다. ASC는 태그를 이 속성에 연결해 적용합니다.|Health,MaxHealth,Mana,MaxMana,Stamina,MaxStamina:현재 자원과 최대치;Level,Experience,MaxExperience:캐릭터 레벨과 경험치;Strength,Intelligence,Arcane,Armor:전투·쿨다운 계산 수치;Burn,Frostbite,ElectricShock:상태별 피해 보너스;IncomingDamage,OutgoingDamage:피해 처리 중간값
UAbilityGrantAndInputManager|입력 전달과 능력 부여|ASC 실행 상태|누름은 즉시 전달하고 Press·그래플처럼 해제가 필요한 대상만 기억합니다. 다음 틱 활성화 경로와 대기 입력 정리를 공통화합니다.|HoldAbilityHandlesByInputTag:해제가 필요한 입력 태그별 능력 핸들;PendingHoldReleases:아직 전달하지 못한 해제;PendingRemoteActivations:ServerInitiated 응답 대기 중 중복 요청 방지
UAbilityCostAndCooldownManager|비용·쿨다운 계산과 적용|Ability 보조 객체|스킬 비용을 적용하고 SkillSource에서 남은 쿨다운을 조회합니다. BasicAttributeSet이 신비 보정 시간을 계산하며 쿨다운 예약 상태는 보관하지 않습니다.|
UAbilityPresentationManager|스킬 시각 표현 실행|Ability 실행 상태|스킬 설정으로 연출을 생성하고 종료 시 정리합니다.|ActiveSkillPresentationActor:현재 스킬 표현 액터;SelfBuffScaleOwner:자기 버프 크기 연출을 적용한 대상의 약한 참조
UCombatComponent|공격 판정과 피해 전달|캐릭터 컴포넌트|무기/맨손 공격의 판정 창, 맞은 대상, 콤보와 추가 피해를 관리합니다.|CombatDamageSettings,UnarmedCombatSettings:피해 계산과 맨손 판정 설정;HitActorsInCurrentUnarmedAttack:한 공격에서 중복 타격을 막을 대상 목록;TemporaryWeaponDamageBonuses,ActiveComboDamageMultiplier:임시 무기 추가 피해와 현재 콤보 배율
UAttackAbility|일반 공격과 콤보|Ability 인스턴스|입력 버퍼와 공격 판정 구간을 관리하며 CombatComponent를 통해 타격을 실행합니다.|AttackingEffectClass:공격 중 적용할 효과 클래스;AttackInputWindowStartEventTag,AttackInputWindowEndEventTag:추가 콤보 입력을 받는 구간 이벤트;AttackDamageWindowStartEventTag,AttackDamageWindowEndEventTag:타격 판정을 켜고 끄는 이벤트;ComboDamageMultiplierPerStep,BufferedJumpSectionName:콤보 단계 피해 배율과 예약한 다음 몽타주 섹션;bAttackDamageWindowActive,WaitInputPressTask:현재 타격 구간 활성 상태와 입력 대기 태스크
AProjectileBase|월드 이동과 적중 효과|Actor 런타임|전달받은 피해·상태 이상 Spec을 적중 대상에 적용하고 액션에 충돌을 알립니다. 상태 누적 적용이 성공하면 대상의 복제 컴포넌트에 추적을 요청합니다.|TargetLocation,Speed:목표 위치와 속도;DamageEffectSpecHandle,DebuffEffectSpecHandle:적중 시 적용할 피해·누적 효과 Spec;StatusEffectDefinition:스택 효과 규칙;OnSkillImpact:충돌 대상과 HitResult를 액션에 전달
UCharacterDeathComponent|사망과 재사용 준비|캐릭터 컴포넌트|사망을 한 번 처리하고 충돌·이동·표현 상태를 복구할 정보를 보관합니다.|Settings:사망 연출과 복구 정책;bDeathHandled:사망 중복 처리 방지 상태
UStatusEffectDefinition|상태 이상 누적·발동 규칙|설정 Data Asset|적중 때 누적하는 Stack 효과와 임계치 도달 후 발동하는 Status 효과를 구분합니다. 피해 수치·지속시간과 UI 아이콘을 보관합니다.|StackTag,StackGameplayEffectClass,MaxStackCount:누적 효과 식별·클래스·발동 임계치;StatusEffectTag,StatusEffectClass:발동 상태 식별·효과;StatusDuration,DamageMagnitude:발동 지속시간과 보정 전 피해;Icon,IconBackgroundColor:아이콘과 게이지 색상
UStatusEffectReplicationComponent|누적 스택 수명과 복제|캐릭터 컴포넌트|ASC의 누적 효과를 추적하고 스택 변화를 복제합니다. 최대 스택 수명 20초와 대기 1초 기준으로 감소를 계산하며 UI가 복제된 스택을 구독합니다.|ReplicatedStacks:태그별 복제 스택 수;StatusEffectDecayStates:감소 시작·진행 상태;TrackedActiveEffects:효과별 스택 변경 구독;BoundAbilitySystemComponent:추적할 ASC

UInventoryComponent|소유 아이템과 장비 슬롯|PlayerState 컴포넌트|아이템 인스턴스 목록과 퀵슬롯·장비 슬롯을 관리하고 변경 목록을 복제합니다.|AllItemList,ReplicatedEntries:소유 아이템 목록과 복제 항목;ConsumableQuickSlotItemIds:소모품 퀵슬롯의 아이템 GUID;WeaponIdsByLoadoutSlot:로드아웃 방향별 무기 GUID;EquippedItemSlots:장착 슬롯과 아이템 연결
UItemInstance|개별 아이템 상태|플레이어 런타임|공통 아이템 정의와 개별 아이템의 수량·강화·식별자를 묶습니다.|ItemDefinition:아이템 공통 이름·기본 스탯·무기 설정;ItemId,Quantity,UpgradeLevel:개별 GUID·수량·강화 단계;Map_EnhancedStat_Magnitude:이 인스턴스의 강화 스탯 수치
UItemDefinition|아이템 공통 규격|설정 Data Asset|아이템 표시 정보, 기본/소모 효과, 판매 정보와 무기 실행 설정의 원본입니다.|DisplayName,Description,IdTag:이름·설명·분류 태그;Map_Stat_Magnitude:기본 스탯 태그 → 수치;ConsumeGameplayEffectClass,Map_Consume_Magnitude,QuantityToConsume:사용 효과·수치·소모 수량;WeaponData:장착·공격·이동·투사체 등 무기 설정;ShopData:상점 상품 설정
UEquipmentComponent|장비 상태를 몸체에 적용|캐릭터 컴포넌트|인벤토리의 선택을 무기 액터와 적용 스탯으로 변환합니다.|CurrentWeaponActor,CurrentWeaponDefinition,CurrentWeaponId:현재 무기 액터·공통 정의·개별 GUID;CurrentWeaponStatSnapshot,EquippedItemsStatSnapshot:현재 적용한 무기/장비 스탯 스냅샷
AWeaponBase|공통 무기 판정과 표현|Actor 런타임|ItemDefinition의 무기 설정을 사용하고 한 공격의 충돌·피해·연출 문맥을 관리합니다.|SourceItemDefinition:이 무기를 만든 아이템 정의;HitActorsInCurrentAttack:현재 공격에서 이미 맞은 액터
UPlayerRewardComponent|보상 요청과 에셋 로드|PlayerState 컴포넌트|플레이어 처치·몬스터 보상을 설정 에셋에 따라 지급하고 로드 대기 요청을 관리합니다.|PlayerKillRewardDefinition,LoadedPlayerKillRewardDefinition:플레이어 처치 보상 설정과 로드 결과;PendingPlayerKillRewards:설정 로드 중 누적한 처치 보상 요청 수
URewardDefinition|처치·승리·상자 보상 규칙|설정 Data Asset|몬스터 처치, 플레이어 처치, 승리와 보상 알림 정책을 분리해 정의합니다.|ChestSpawn,MonsterDefeatReward:상자 생성과 몬스터 처치 보상;PlayerKillReward,GameVictoryReward:플레이어 처치와 승리 보상;Notification:보상 알림 설정
UDefaultPlayerProvisioner|기본 지급 절차|매치/로비 서비스|기본 지급 에셋을 로드하고 모드별 아이템·판도라·포인트를 초기화합니다.|ProvisionDefinition:기본 지급 정책 에셋;Mode:적용할 지급 모드
UDefaultProvisionDefinition|시작 아이템·판도라 설정|설정 Data Asset|시작할 때 지급할 수치와 콘텐츠 목록을 정의합니다. 플레이 중 현재 소유 목록은 각 컴포넌트가 보관합니다.|PandoraGrants,ItemGrants,GestureGrants:초기 판도라·아이템·제스처 지급 목록;StatusPointValues,SoulDustValues:모드별 시작 스탯 포인트와 판도라 성장 재화;GrantAllWeapons,GrantAllEquipment:모드별 전체 무기/장비 지급 정책

AExperienceGameMode|서버 매치 책임 분배|서버 GameMode|매치 진행, 스폰, 플레이어 준비를 별도 컴포넌트로 나눕니다.|MatchFlowComponent,SpawnComponent,PlayerProvisioningComponent:매치·스폰·초기 지급 담당;MatchRuleDefinition:적용할 매치 규칙 에셋
AExperienceGameState|매치 공용 상태|GameState / 복제|선택한 Experience와 매치 시간 정보를 클라이언트에서 읽을 공용 상태로 제공합니다.|ExperienceManagerComponent:Experience 로드 상태 관리;MatchRuleDefinition,MatchTimerState:매치 규칙과 시간 상태;GameResultWidgetClass:결과 화면 클래스
UExperienceManagerComponent|Experience 로딩 상태 머신|월드 런타임|Experience 에셋과 필요한 Game Feature 플러그인을 로드하고 준비/실패 이벤트를 보냅니다. Loaded는 해당 월드의 준비 상태입니다.|CurrentExperienceId,CurrentExperience:선택한 Experience ID와 로드 결과;LoadState:Unloaded부터 Loaded/Failed/Deactivating까지의 진행 상태;GameFeaturePluginURLs:활성화할 기능 플러그인 URL 목록
UExperienceDefinition|플레이 모드 구성|설정 Data Asset|어떤 Pawn을 기본으로 사용할지와 활성화할 Game Feature 목록을 정의합니다.|DefaultPawnClass:기본 플레이어 Pawn 클래스;GameFeaturesToEnable:이 Experience에서 켤 기능 플러그인 이름
UExperienceMatchFlowComponent|타이머·승패 진행|서버 매치 컴포넌트|매치 타이머, 골든킬과 결과 표시의 진행 상태를 관리합니다.|Settings:매치 진행에 적용한 설정;bServerMatchTimerStarted,bMatchTimerExpired:서버 타이머 시작/만료 상태;bGoldenKillActive,GoldenKillVictoryScore,bGameResultShown:골든킬 진행·승리 점수·결과 화면 표시 상태;RuntimeContentPreloadHandle,bRuntimeContentLoadPending:런타임 콘텐츠 비동기 로드 수명
UExperienceSpawnComponent|스폰 지점과 리스폰|서버 매치 컴포넌트|플레이어별 시작 지점 배정과 초기 위치를 보관해 스폰/리스폰에 사용합니다.|Settings:스폰 정책 설정;UsedPlayerStarts,AssignedPlayerStartsByController:사용한 시작 지점과 Controller별 배정;InitialPlayerSpawnTransforms:플레이어의 초기 스폰 변환
UExperiencePlayerProvisioningComponent|입장 플레이어 준비|서버 매치 컴포넌트|프로필 복원과 기본 지급이 완료된 플레이어를 관리합니다.|PlayerProfileService,DefaultPlayerProvisioner:프로필 적용 서비스와 초기 지급 서비스;PendingGameplayPlayers,ReadyGameplayPawns:준비 대기 플레이어와 완료된 Pawn
UPlayerMatchComponent|매치 식별과 사망 기록|PlayerState 컴포넌트|닉네임·플레이어 키·팀 같은 식별 정보와 현재 매치 상태를 제공합니다.|PlayerMatchIdentity:플레이어 식별·닉네임·팀/스폰 슬롯 정보;DeathCount,PlayerMapRegion:현재 매치 사망 수와 맵 영역
UMatchRuleDefinition|로비·매치·리스폰 규칙|설정 Data Asset|시작 카운트다운, 제한 시간, 골든킬과 리스폰 정책을 정의합니다.|LobbyStartCountdownSeconds,MatchTimerSeconds:로비 시작 대기와 매치 제한 시간;MapsWithoutMatchTimer,bGoldenKillEnabled:타이머 제외 맵과 골든킬 활성 정책;PlayerRespawnDelay,bUseRandomPlayerStartRespawns,RandomRespawnPlayerStartTags:리스폰 대기와 랜덤 시작 지점 선택 정책;TeamOverlayMaterials,HudTickInterval:팀 표현 머티리얼과 HUD 갱신 간격
ULevelDefinition|이동 가능한 맵 설정|설정 Data Asset|플레이 가능한 맵 목록과 각 화면의 월드 에셋을 연결합니다.|IngameLevels:로비에서 선택하는 게임 맵 옵션 목록;TitleLevel,LobbyLevel,RoomLevel,TrainingLevel:타이틀·로비·방·훈련 화면의 월드 소프트 참조
UGameFeatureAction_AddAbilities|기능 활성화 시 능력 부여|Game Feature 액션|대상 Actor 클래스에 정의된 능력을 부여하고 기능 수명에 맞춰 핸들을 정리합니다.|TargetClass,Abilities:대상 클래스와 부여할 능력 항목;ContextHandles:월드/컨텍스트별 적용 핸들
UGameFeatureAction_AddActorExtension|기능 활성화 시 Actor 확장|Game Feature 액션|기능 액션의 조건과 역할에 맞춰 Actor 확장을 활성화/비활성화합니다.|TargetClass,Extension:대상 클래스와 적용할 확장 구성;ContextHandles:컨텍스트별 등록 수명 추적

UOnlineSessionsSubsystem|온라인 방 생성·검색·입장|게임 인스턴스 서비스|OnlineSubsystem 세션 인터페이스를 호출하고 비동기 요청의 결과·취소·타임아웃을 관리합니다.|SessionInterface,ActiveSessionSearch:플랫폼 세션 인터페이스와 검색 객체;PendingRoomName,PendingMapName:진행 중 요청에 사용할 방 이름과 맵 이름;ActiveSessionRequestId,ActiveSessionRequestKind,SessionOperationState:진행 중 비동기 요청 ID·종류·단계;bActiveRequestCancelRequested,SessionOperationTimeoutSeconds:요청 취소 상태와 작업 제한 시간
UControllerSessionComponent|플레이어의 세션 종료 경로|Controller 컴포넌트|플레이어가 방을 나갈 때 세션 파괴와 화면 이동을 연결합니다. 자체 추가 저장 필드는 없습니다.|
ULobbyRuntimeSubsystem|로비와 맵 이동 사이 캐시|게임 인스턴스 캐시|로비 설정과 플레이어의 매치 식별·외형·판도라 정보를 이동 구간에 전달합니다. 디스크 저장은 ProfileSubsystem의 별도 책임입니다.|LobbyRuntimeConfig:현재 로비 실행 설정;LoadedLevelDefinition:로드한 맵 설정
ULobbyMatchCoordinator|로비 시작 조건과 카운트다운|서버 로비 서비스|시작 조건을 검사하고 카운트다운과 시작 요청 상태를 관리합니다.|StartCountdownTimerHandle:시작 카운트다운 타이머;bGameStartRequested:게임 시작 요청이 진행 중인지 여부
ULobbyTravelCoordinator|세션 시작 후 맵 이동|서버 로비 서비스|콘텐츠/온라인 세션 시작을 기다린 뒤 준비한 주소로 ServerTravel을 진행합니다.|PendingTravelUrl:이동할 맵과 옵션을 담은 URL;StartSessionCompleteHandle:비동기 세션 시작 완료 콜백 핸들
ALobbyGameMode|서버 로비 책임 분배|서버 GameMode|로비 설정, 시작 조건, 기본 지급과 게임 맵 이동을 각각의 담당자에 연결합니다.|MatchCoordinator,TravelCoordinator:시작 판단과 실제 이동 담당;DefaultPlayerProvisioner:로비 기본 지급 담당
ALobbyGameState|공유 로비 표시 상태|GameState / 복제|선택한 맵과 시작 예정 시각을 클라이언트 UI에 제공합니다.|SelectedMapOption:현재 선택한 맵 옵션;bStartPending,GameStartEndServerTimeSeconds:시작 대기 여부와 서버 기준 카운트다운 종료 시각;ExperienceManagerComponent:로비 Experience 로드 상태
ULobbyConfigurationComponent|로비 설정 에셋 로드|서버 로비 컴포넌트|맵·규칙·기본 지급 정의를 로드하고 현재 로비 구성의 유효성을 확인합니다.|LoadedLevelDefinition,LoadedMatchRuleDefinition,LoadedDefaultProvisionDefinition:로드 완료된 맵·매치·초기 지급 설정;RuntimeState:현재 로비 설정 상태
ULobbyPlayerStateComponent|로비 이탈·닉네임 보조 상태|PlayerState 컴포넌트|로비 이탈 여부와 닉네임 표시 힌트를 관리합니다. 정식 매치 식별 데이터는 PlayerMatchComponent에 있습니다.|bLeavingLobby:로비를 떠나는 중인지 여부;NicknameHint,bUsingNicknameHint:닉네임 힌트와 사용 여부
ULobbyWidget|로비 사용자·맵·시작 화면|로컬 UI|로비 사용자 목록, 맵 정보와 시작 카운트다운을 화면에 표현합니다.|LobbyUsers:현재 표시하는 로비 사용자 항목;Txt_SelectedMapName,Img_SelectedMapThumbnail,Txt_GameStartCountdown:선택 맵 이름·썸네일·시작 카운트다운 표시 위젯;ActiveGameConfigWidget,GameStartCountdownTickHandle:열린 설정 화면과 카운트다운 갱신 타이머

AEnemyBase|적 공통 몸체와 ASC|적 Actor 런타임|자체 능력 시스템과 전투/트레이닝 컴포넌트를 만들고 EnemyDefinition을 로드합니다.|EnemyDefinition,LoadedEnemyDefinition:적 설정 참조와 로드 결과;AbilitySystemComponent:적이 소유하는 ASC;EnemyCombatComponent,EnemyTrainingBotComponent:적 공격과 트레이닝 동작 담당;StartingWeaponDefinition:시작 무기 아이템 정의
AMonsterCharacter|몬스터 공격·피해·보상|적 Actor 런타임|적 공통 몸체 위에서 몬스터 공격 구간, 피해 대상, 사망과 처치 보상을 처리합니다.|ResolvedMonsterMaxHealth:몬스터 최대 체력 설정;AttackDamageMagnitude,AttackSphereActiveDuration:몬스터 공격 피해와 판정 구간 시간;MonsterRewardDefinition,LastDamagingPlayerState:처치 보상 설정과 마지막으로 피해를 준 플레이어;AttackHitActorsThisSwing,bAttackWindowOpen,bDying:현재 공격의 중복 타격 목록·판정 활성·사망 상태
AMonsterAIController|몬스터 StateTree와 인지|AI Controller|주변 플레이어 인지와 StateTree 실행을 연결합니다. Behavior Tree 서비스/태스크는 별도의 적 BT 경로입니다.|PerceivedPlayerPawn:인지한 플레이어 Pawn;ResolvedMonsterStateTree:로드한 몬스터 StateTree
UEnemyBaseDefinition|적 전투·훈련·표현 설정|설정 Data Asset|적 공격 정책과 훈련 봇 동작, 몬스터 표시·체력·StateTree를 정의합니다.|Combat,TrainingBot,MonsterPresentation:전투·훈련·몬스터 표현 설정;MonsterStateTree,MonsterMaxHealth:실행할 StateTree와 몬스터 체력 설정
UEnemyCombatComponent|적의 공격 대상과 실행|적 컴포넌트|적 전투 설정을 적용하고 공격 대상으로 타격을 실행합니다.|Settings:적 전투 설정;AttackTarget:현재 공격 대상
UEnemyTrainingBotComponent|훈련 봇 피격·복구|적 컴포넌트|훈련 봇의 경직, 장비 교체와 리스폰 상태를 관리합니다.|Settings:훈련 봇 동작 설정;RespawnTransform:복구할 위치·회전·크기;PendingWeaponDefinition:교체를 기다리는 무기 정의
UBTService_UpdateEnemyTarget|BT 대상 정보를 갱신|Behavior Tree 서비스|블랙보드에 대상·거리·시야·무기 상태를 갱신해 적 행동 판단에 제공합니다. MonsterAIController의 StateTree와는 구분되는 BT 경로입니다.|TargetActorKey,LastKnownTargetLocationKey:대상과 마지막 위치를 기록할 블랙보드 키;DistanceToTargetKey,AttackRangeKey,HasRangedWeaponKey,HasLineOfSightKey:거리·사거리·원거리 무기·시야 결과를 기록할 블랙보드 키;bAutoAttackWhenInRange,AutoAttackInterval:사거리 내 자동 공격 여부와 간격
UBTTask_EnemyAttack|BT 공격 행동 요청|Behavior Tree 태스크|대상 거리와 이동 정책을 검사하고 적 공격을 요청합니다.|bRequireTargetInAttackRange,bMoveToTargetWhenOutOfRange,bStopMovementBeforeAttack:사거리 조건·접근 이동·공격 전 정지 정책

UPlayerProfileSubsystem|프로필 로드와 저장 예약|로컬 영구 저장 서비스|플레이어별 SaveGame과 저장 스냅샷, 변경 상태를 관리해 비동기 저장을 조정합니다.|SaveSnapshotsByPlayerId:플레이어 ID별 저장 시점 스냅샷;SavedGameByPlayerId:플레이어 ID → 메모리의 실제 UPdSaveGame;DirtyPlayerIds,SaveInFlightPlayerIds:변경되어 저장할 ID와 현재 저장 중인 ID;SaveDeadlinesByPlayerId,SaveRetryCountsByPlayerId:저장 예정 시각과 재시도 횟수
UPdSaveGame|디스크에 남는 플레이어 기록|영구 저장 데이터|골드·통계·업적·매치 기록과 판도라/스킨 소유 데이터를 저장합니다. 런타임 UObject 포인터 대신 판도라 ID와 레벨·방향별 ID를 기록합니다.|ProfileDataVersion,SaveId,SaveRevision:데이터 버전·저장 식별자·리비전;Gold:보유 골드;PlayerPandoraData:판도라 ID → 레벨, 선택 ID, 방향별 ID, 남은 포인트;PlayerSkinData,MatchRecords,SelectedAchievementId:스킨 보유 정보·매치 기록·선택 업적
UProfileSaveEnvelope|저장 파일 포장 형식|영구 저장 컨테이너|직렬화한 프로필 바이트를 난독화하고 CRC로 손상을 검사하는 포장입니다. 암호화나 인증을 보장하는 구조는 아닙니다.|StorageFormatVersion,ObfuscationNonce,PlainPayloadCrc:포맷 버전·난독화 nonce·원문 CRC;ProfileSaveId,ProfileRevision:내부 프로필과 맞출 식별자·리비전;ObfuscatedPayload:난독화한 직렬화 바이트 배열
UControllerProfileSyncComponent|프로필 외형을 서버로 전달|Controller 동기화 상태|로컬 프로필의 외형 정보를 서버에 동기화하고 재시도/업적 콜백 수명을 관리합니다.|LastRemoteSkinSyncRequestTime:마지막 원격 스킨 동기화 시각;LocalCosmeticProfileSyncTimerHandle,LocalCosmeticProfileSyncAttemptCount:외형 동기화 재시도 타이머와 횟수;SteamAchievementStateChangedHandle:Steam 업적 변경 구독 핸들
UExperiencePlayerProfileService|입장 시 프로필 적용|매치 서비스|게임 입장 시 프로필·식별 정보를 읽고 플레이어 컴포넌트에 적용합니다. 자체 저장 파일을 보관하지 않습니다.|bAssignDefaultTeamWhenLobbyTeamMissing,DefaultLobbyTeamColorIndex:로비 팀 정보가 없을 때의 기본 팀 배정 정책

UUiSubsystem|화면 생성과 모달 입력|로컬 UI 서비스|위젯 설정을 로드하고 모달 입력과 연결 중 화면의 수명을 관리합니다.|ModalInputStack:모달 화면의 입력 모드 스택;StatusViewModel:상태 표시용 ViewModel;WidgetClassDefinition,ConfiguredWidgetClassDefinition:현재 적용한 화면 클래스 설정과 구성된 기본 정의;InputStateBeforeModals,RestorePolicyAfterModals:모달을 열기 전 입력 상태와 닫은 뒤 복구 정책
UHudUiRouter|HUD 화면·메뉴 배치|로컬 UI 라우터|HUD에 메뉴·화면·스코어보드 계층을 연결하고 모달 입력 토큰을 관리합니다.|OwnerHud:화면을 소유한 HUD의 약한 참조;ModalInputToken:이 라우터가 확보한 모달 입력 토큰
UInfoLoadoutStore|정의 기반 로드아웃 UI 캐시|표시용 캐시|인벤토리·판도라 컴포넌트를 구독합니다. 무기는 ItemInstance로, 판도라는 PandoraDefinition 참조로 방향별 선택을 표시합니다.|BoundInventoryComponent,BoundPandoraComponent:게임 원본 구독 대상;LeftWeapon,UpWeapon,RightWeapon:방향별 무기 인스턴스;LeftPandoraDefinition,UpPandoraDefinition,RightPandoraDefinition:방향별 판도라 정의
UInfoUiPresenter|정보 화면 구성 연결|로컬 UI Presenter|로드아웃 저장소와 각 정보 탭 Presenter를 묶어 화면 갱신을 조정합니다.|LoadoutStore:표시용 로드아웃 스냅샷;PandoraPresenter:판도라 탭의 선택·필터·표시 담당
UInfoPandoraTabPresenter|판도라 탭 선택과 필터|로컬 UI Presenter|선택한 장착 슬롯과 필터로 판도라 목록을 구성하고 컴포넌트 변경을 화면에 반영합니다.|SelectedEquipSlot,CurrentFilterTag:화면에서 선택한 장착 슬롯과 필터 태그;LoadoutStore,BoundPandoraComponent:로드아웃 캐시와 구독한 원본 컴포넌트
UPandoraWidgetViewModel|판도라 카드 표시값|MVVM 표시 데이터|판도라 정의와 성장 상태를 이름·아이콘·잠금/포인트 가능 상태로 변환한 화면 데이터입니다.|DisplayName,LevelText,IconBrush:카드에 표시할 이름·레벨·아이콘;bCanSpend,bIsLocked,bNotEnoughPoints,bAtMaxLevel:성장 버튼과 잠금 표시를 결정할 상태
UPandoraDescriptionViewModel|판도라 상세 설명 표시값|MVVM 표시 데이터|판도라 설명, 무기 조건과 스킬 이름·아이콘·설명을 화면용 값으로 만듭니다. 실제 스킬 정의는 PandoraDefinition의 Skills 배열을 따라 읽습니다.|TitleText,DescriptionText,WeaponRequirementText:판도라 제목·설명·호환 무기 문구;CurrentLevelDescriptionText,NextLevelDescriptionText,PointsRequiredText:현재/다음 단계 설명과 필요한 포인트;SkillNameText1,SkillDescriptionText1,SkillIconResource1:첫 번째 스킬의 이름·설명·아이콘. 같은 표시 필드가 다른 슬롯에도 존재
UHealthBarViewModel|체력·경험치를 화면으로|MVVM 표시 데이터|ASC 속성 변화를 체력/경험치 수치·비율·문구로 변환합니다. 이 값을 바꿔도 게임의 실제 체력이 바뀌는 구조는 아닙니다.|Health,MaxHealth,HealthPercent,HealthText:체력 숫자·비율·표시 문구;CurrentExperience,MaxExperience:경험치 표시용 값
UAbilitiesBarWidget|스킬 슬롯 목록 화면|로컬 UI|ASC의 부여 능력과 판도라 성장 상태를 읽어 스킬 슬롯을 구성합니다.|MinimumSlots,PandoraSkillSlots:화면 최소 슬롯과 판도라 슬롯 수;CachedAbilitySystemComponent,BoundPandoraTreeComponent:능력/성장 상태를 구독하는 대상
UAbilitySlotWidget|스킬 아이콘·출처별 쿨다운|로컬 UI|AbilitySpec의 SkillSource를 통해 스킬 정의와 남은 쿨다운을 읽습니다. 쿨다운 태그는 갱신 통지에 쓰고 실제 시간은 출처에 해당하는 ASC 활성 효과에서 조회합니다.|AbilitySpecHandle,AbilityObjectRef:화면 슬롯의 능력 핸들과 객체;SkillSlotIndex,TotalCooldownTime:슬롯 인덱스와 화면 표시용 전체 쿨다운;BoundCooldownTag:쿨다운 변화 구독 태그
UWidgetClassDefinition|화면 클래스와 스타일 목록|설정 Data Asset|생성할 HUD·메뉴·결과·캐릭터 UI 클래스와 공통 스타일을 정의합니다.|Style,InputIcons,MapUI:공통 스타일·입력 아이콘·맵 UI 설정;PlayerHudWidgetSettings,MenuPopupWidgetSettings,GameResultWidgetSettings:HUD·메뉴·결과 화면 구성
UShopWidget|상점 목록과 구매 선택|로컬 UI|상점 설정을 로드해 상품 목록을 구성하고 선택 상품과 분류를 관리합니다.|ShopCatalogDefinition:상점 이름·상품 목록 설정;ShopProductList:상점 상품 목록;EntryDataList,SelectedEntryData,ActiveCategory:화면 항목·선택 항목·현재 분류
UShopCatalogDefinition|상점 판매 목록 설정|설정 Data Asset|상점 이름·설명과 판매할 상품 참조 목록, 전체 판도라/스킨 포함 여부를 정의합니다.|ShopName,ShopDescription:상점 이름·설명;ProductList:상품 종류와 콘텐츠 참조 목록
USkillAbility|스킬 액션 트리 실행기|Ability 인스턴스|시작 시 비용을 한 번 확정하고 Action을 복제합니다. Duration은 활성화 시 계산한 종료 시점을 공유하며, 정상 종료 시 사용 횟수 조건에 따라 쿨다운을 적용합니다.|ActiveAction:이 시전만의 복제 액션 트리;ActivationTime,DurationEndTime:활성화 시각과 공통 종료 시점;DurationTimer:Duration 만료 또는 Press 최소 유지 종료 예약;UsesSinceCooldown,bSkillCommitted:쿨다운까지 누적 사용 횟수와 이번 시전 확정 여부
USkillAction|액션의 공통 실행 문맥|액션 템플릿 / 시전 복제본|에셋의 트리를 복제한 뒤 실행합니다. 각 액션은 실행기 약한 참조와 대상·위치·이벤트 문맥을 공유하며 완료·취소를 전달합니다.|OwningAbility:공통 GAS 기능과 종료 시점을 제공하는 SkillAbility;ExecutionContext:TargetActor·Transform·EventData;OnFinished,bRunning:완료 통지와 실행 상태
USkillSequenceAction|액션 순차 실행|액션 템플릿 / 시전 복제본|앞 액션의 결과 문맥을 다음 액션에 전달합니다. 실패하면 뒤 단계는 실행하지 않습니다.|Actions:순서대로 실행할 자식 액션 템플릿;NextIndex:다음에 실행할 자식 위치
USkillParallelAction|액션 병렬 실행|액션 템플릿 / 시전 복제본|같은 문맥으로 자식을 시작하고 모두 끝나면 완료합니다. 하나가 실패하면 나머지를 정리합니다.|Actions:동시에 시작할 자식 액션;Remaining:아직 완료하지 않은 자식 수
USkillRepeatAction|액션 반복 실행|액션 템플릿 / 시전 복제본|반복마다 자식 템플릿을 복제합니다. Count·Interval과 SkillAbility의 공통 종료 시점을 검사해 반복을 끝냅니다.|Action:반복할 자식 템플릿;Count,Interval:반복 횟수와 간격. Count 0은 Ability 종료까지;Current:현재 반복의 복제 액션;CompletedCount,Timer:완료 횟수와 다음 반복 예약
USkillProjectileCastAction|투사체 조준과 발사 액션|액션 템플릿 / 시전 복제본|투사체 전용 Ability 대신 SkillAction이 조준·차징·연속 발사를 맡습니다. GAS 비용·피해 Spec은 SkillAbility의 공통 기능을 사용합니다.|Settings:투사체 속도·궤적·생성·조준·연출 설정;ReadiedProjectile:발사 준비 중인 투사체;TargetDataTask,ConfirmCancelTask:조준 대상과 확정/취소 대기;SocketBarrageProjectiles,SocketBarrageTimerHandle:연속 발사 대기 액터와 간격 타이머
UReactiveStatusEffectAbility|스택 임계치의 상태 이상 발동|반응형 Ability 인스턴스|효과 적용을 감시해 누적 스택이 최대치에 도달하면 실제 상태 이상 효과를 적용하고 성공 시 누적 스택을 제거합니다. 피해 Spec은 BasicAttributeSet의 공통 계산을 사용합니다.|StatusEffectDataAsset:누적/발동 태그·임계치·효과·피해 규칙;WaitGameplayEffectAppliedTask:대상에게 효과가 적용될 때의 감시 작업
UStatusEffectWidget|상태 이상 누적·잔여 시간 표시|로컬 UI Widget|복제된 스택과 ASC의 발동 효과를 읽어 두 게이지로 표시합니다. 스택 감소는 NativeTick에서 공통 수명 기준으로 보간합니다.|EffectDataAsset:아이콘·색상·태그·최대 스택 정의;CurrentStackCount:화면이 받은 누적 스택;BoundStatusEffectReplicationComponent:스택 변경 구독 대상;StackFillDecreaseStartTime,StackFillDecreaseStartPercent:Tick 보간의 시작점;EffectFillMeter,EffectAppliedTimeLeft:누적 게이지와 발동 상태 잔여 시간
'''

def notes():
    result = {}
    for raw in NOTES.splitlines():
        if not raw.strip():
            continue
        name, role, storage, purpose, groups = raw.split('|')
        fields = []
        for group in groups.split(';'):
            if group:
                keys, meaning = group.split(':', 1)
                fields.append({'keys': keys.split(','), 'meaning': meaning})
        result[name] = dict(role=role, storage=storage, purpose=purpose, highlights=fields)
    assert len(result) == 100
    return result
