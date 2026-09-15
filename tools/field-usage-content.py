"""Field-level intent, with explicit notes for easily misunderstood data ownership."""
import re

NOTES = '''
USkillDefinition.Description|스킬 툴팁과 판도라 상세 화면에 표시할 설명 원문입니다. UI 데이터 Builder와 스킬 설명 위젯이 읽어 표시 문구를 구성합니다.
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
APdPlayerState.StatUpgradeComponent|스탯 정의의 로드와 서버 기본값 초기화 시점, 투자·환불 요청을 담당합니다. 계산은 StatUpgradeDefinition이, 실제 GAS 적용은 ASC가 맡도록 연결합니다.
UPdAbilitySystemComponent.GrantedPandoraSkillSources|AbilitySpec이 참조하는 판도라 출처 객체를 유지하고 복제 서브오브젝트로 등록합니다. 더 이상 사용하는 능력이 없을 때 보관·복제 등록을 정리하기 위한 목록입니다.
UPdAbilitySystemComponent.ActivationsWaitingForSource|클라이언트에 판도라 출처가 아직 도착하지 않은 발동을 보류합니다. 출처 복제 후 재시도하고 종료·실패한 발동은 대기 목록에서 제거합니다.
UPdAbilitySystemComponent.AbilityGrantAndInputManager|능력 부여와 입력 태그·핸들 상태 처리를 한 관리자로 위임해 ASC의 입력/능력 콜백에서 재사용합니다.
UPandoraSkillSource.PandoraDefinition|어느 판도라에서 부여된 스킬인지 기억합니다. SkillIndex와 함께 GetSkillDataAsset에서 실제 스킬 정의를 조회합니다. 이 출처 객체 자체가 쿨다운 효과의 SourceObject가 됩니다.
UPandoraSkillSource.SkillIndex|PandoraDefinition.Skills 배열에서 이번 능력의 슬롯을 찾기 위해 보관합니다. GetSkillDataAsset이 정의의 GetSkillDefinition(SkillIndex)을 호출하므로 별도 스킬 포인터를 중복 보관하지 않습니다.
UPandoraSkillSource.PandoraLevel|출처 초기화 시 전달된 레벨을 보관합니다. Binder 경로에서는 스킬 슬롯의 요구 레벨을 전달하므로 Tree에 저장된 플레이어의 현재 성장 레벨과 같은 뜻으로 해석하지 않습니다.
UPandoraSkillSource.LoadoutDirection|능력이 어느 로드아웃 방향에서 부여됐는지 기억해 해당 방향의 판도라 속성 및 피해 계산 문맥을 선택할 때 사용합니다.
UPandoraDefinition.DisplayName|카드·슬롯·상점·설명 화면에서 사용할 판도라 이름입니다. GetDisplayName은 값이 비어 있으면 에셋 이름을 대신 반환합니다.
UPandoraDefinition.Description|판도라의 설명 원문을 보관해 카드·상점·상세 설명용 표시 데이터로 전달합니다.
UPandoraDefinition.IconTexture|판도라를 그림으로 식별할 공통 아이콘 에셋을 참조합니다. 슬롯·장착 버튼·보상 알림에서 같은 아이콘을 사용합니다.
UPandoraDefinition.IdTag|판도라 분류를 태그로 식별해 MatchesPandoraType과 외부 Getter 기반 필터·표시에 사용합니다.
UPandoraDefinition.ActivatableWeaponTags|사용을 허용할 무기 태그들을 보관합니다. 무기 호환 여부를 검사하고 UI에 무기 요구 조건을 표시할 때 읽습니다.
UPandoraDefinition.MaxLevel|모든 판도라의 최대 레벨을 3으로 고정하는 static constexpr 상수입니다. GetMaxLevel·GetFixedMaxLevel, 슬롯 요구 레벨과 해금 범위 검사에 사용합니다. 에셋마다 변경되는 저장값이 아닙니다.
UPandoraDefinition.PointsRequiredPerLevel|레벨별 성장 포인트 비용을 보관합니다. GetRequiredPointsForLevel이 요청 레벨에 해당하는 항목을 읽으며 유효하지 않은 항목은 1로 처리합니다.
UPandoraDefinition.UnlockRules|선행 판도라와 필요한 성장 레벨을 저장합니다. Tree가 해금 가능 여부를 검사하고 설명 화면이 선행 조건을 안내할 때 사용합니다.
UPandoraDefinition.Tier|에셋에 판도라 티어를 기록하는 설정 필드입니다. 최신 C++ 소스에서 이를 사용하는 함수는 확인되지 않습니다.
UPandoraDefinition.ShopData|가격·판매 관련 공통 설정을 담습니다. GetShopData가 상점 처리에 읽기 전용 참조를 반환합니다.
UPandoraTreeComponent.GrantedPandoras|플레이어가 성장시킨 판도라와 현재 레벨을 함께 저장합니다. 해금 조건·현재 레벨 조회, 성장 갱신과 저장/복원에 사용합니다.
UPandoraTreeComponent.PointsAvailable|현재 소비 가능한 판도라 포인트를 유지합니다. 성장 비용을 지불할 수 있는지 검사하고 획득·소비 후 화면에 남은 수량을 알립니다.
UPandoraTreeComponent.InitialGrantedPandoras|트리 초기 구성 시 지급할 판도라와 시작 레벨을 설정합니다. 실행 중 성장 기록인 GrantedPandoras와 구분합니다.
UPandoraTreeComponent.InitialPointsAvailable|트리 초기 구성에 사용할 시작 포인트 수량입니다. 실행 중 잔액인 PointsAvailable의 초기 정책을 제공합니다.
UPandoraComponent.AllPandoraList|표시와 검색에 사용할 PandoraDefinition 목록입니다. 보유 여부를 멤버로 가진 인스턴스 목록은 아니며 보유 판정은 ReplicatedEntries의 IsOwned를 조회합니다.
UPandoraComponent.CurrentPandoraDefinition|현재 선택한 판도라 정의를 참조해 선택 스킬의 부여·입력 연결과 UI 알림에 사용합니다.
UPandoraComponent.PandoraLoadoutSlots|로드아웃 방향별 판도라 정의를 보관해 방향 전환 시 어느 판도라를 선택할지 결정합니다.
UPandoraComponent.GrantedPandoraAbilityHandles|보유한 판도라에서 부여된 능력 핸들을 유지해 전체 초기화·기능 종료 시 회수합니다. 단순 선택 변경은 입력 태그를 바꾸며 기존 시전과 쿨다운 출처를 유지합니다.
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
UPandoraDefinition.Skills|슬롯 순서대로 USkillDefinition을 직접 참조합니다. Getter가 슬롯 범위와 빈 참조를 확인하고 Binder·SkillSource·UI에 스킬 설정을 반환합니다.
UPandoraComponent.ReplicatedEntries|Definition과 IsOwned를 담는 복제 항목 목록입니다. 보유 상태를 서버에서 변경하고 클라이언트 목록·필터·로드아웃에 반영합니다.
USkillDefinition.Action|에셋 안에 편집 가능한 액션 트리 템플릿을 보관합니다. USkillAbility가 활성화할 때 트리 전체를 DuplicateObject하여 시전자별 진행 상태를 분리합니다.
USkillDefinition.Activation|시전 조건·실행 중 소유 태그·차단/취소 태그·Press 입력 해제 정책·쿨다운당 사용 횟수를 묶습니다. Binder가 Spec 태그를 구성하고 SkillAbility가 시전 조건과 종료 정책에 적용합니다.
USkillDefinition.Time|CooldownDuration은 종료 시 적용할 쿨다운의 기본 시간이고 Duration은 준비·조준·몽타주까지 포함한 전체 스킬 시간입니다. SkillAbility가 활성화 시 DurationEndTime을 계산합니다.
USkillAbility.ActiveAction|정의의 Action을 복제한 이번 시전의 루트입니다. 완료 콜백을 연결해 결과에 따라 Ability를 끝내고, 종료·취소 때 전체 트리의 대기 작업을 정리합니다.
USkillAbility.ActivationTime|이번 활성화가 시작된 월드 시각입니다. Duration 종료 시점 계산과 Press 입력의 최소 유지 시간 계산에 사용합니다.
USkillAbility.DurationEndTime|Duration 스킬의 하나의 절대 종료 시점입니다. -1은 기한 없는 종료 정책을 뜻하며 액션·반복·연출이 GetRemainingDuration으로 같은 남은 시간을 읽습니다.
USkillAbility.DurationTimer|Duration 만료 또는 Press 최소 유지 시간 도달 시 Ability를 끝낼 타이머입니다. Ability가 끝나면 타이머도 해제합니다.
USkillAbility.bSkillCommitted|이번 시전이 비용을 이미 확정했는지 기록해 여러 액션이 CommitSkill을 호출해도 한 번만 차감합니다. 정상 종료의 쿨다운 적용 조건으로도 확인합니다.
USkillAbility.UsesSinceCooldown|쿨다운까지 허용되는 연속 사용 횟수를 추적합니다. 정의의 UsesPerCooldown과 레벨 배율 기준에 도달하면 0으로 되돌리고 정상 종료 시 쿨다운을 적용합니다.
USkillAction.OwningAbility|이번 액션의 실행기를 약하게 참조합니다. 파생 액션이 GetAbility로 공통 GAS 작업·피해 생성·남은 시간에 접근하며 실행기를 소유하지는 않습니다.
USkillAction.ExecutionContext|현재 대상 Actor·Transform·GameplayEventData를 묶습니다. 결과 문맥을 다음 액션에 전달해 이벤트 대기·조준·투사체 적중 이후 단계를 같은 트리로 연결합니다.
USkillAction.OnFinished|이 액션의 성공·실패 완료를 부모 액션이나 SkillAbility에 전달하는 델리게이트입니다. 순차 진행·병렬 잔여 수·Ability 종료를 연결합니다.
USkillAction.bRunning|중복 시작·완료·취소를 막는 실행 플래그입니다. 자식 정리나 콜백 시 이미 종료된 액션이 다시 진행되지 않도록 검사합니다.
USkillSequenceAction.Actions|앞에서부터 실행할 자식 액션 배열입니다. 이전 자식의 결과 문맥을 다음 자식에 전달하고 실패하면 나머지 진행을 중단합니다.
USkillSequenceAction.NextIndex|다음에 시작할 자식의 배열 위치를 기억합니다. 자식 완료 콜백에서 다음 위치를 이어 실행하고 배열 끝이면 완료합니다.
USkillParallelAction.Actions|동시에 시작하는 자식 액션 배열입니다. 모든 자식에 같은 초기 문맥을 주며 실패·취소 시 실행 중인 자식을 함께 정리합니다.
USkillParallelAction.Remaining|아직 완료하지 않은 자식 수입니다. 자식 완료마다 감소시켜 모두 끝난 시점을 판단합니다.
USkillRepeatAction.Action|반복의 원본 자식 템플릿입니다. 매 반복 DuplicateObject로 Current를 새로 만들어 이전 반복의 상태가 남지 않게 합니다.
USkillRepeatAction.Current|지금 실행 중인 반복 자식 복제본입니다. 완료를 구독하고 반복 중단이나 부모 취소 시 이 객체를 정리합니다.
USkillRepeatAction.Count|실행할 총 반복 횟수입니다. 0이면 횟수 제한 없이 Ability 수명 안에서 반복하고 양수면 CompletedCount와 비교합니다.
USkillRepeatAction.Interval|자식 완료 뒤 다음 반복을 예약할 간격입니다. 실행기의 공통 지속시간이 끝나면 새 반복을 시작하지 않습니다.
USkillRepeatAction.CompletedCount|끝낸 반복 수를 누적해 Count 도달 여부를 검사합니다. 새로 시작할 때 초기화합니다.
USkillRepeatAction.Timer|다음 반복 예약을 취소·정리하기 위한 타이머 핸들입니다. 중단된 시전에서 지연 콜백이 계속 실행되지 않게 해제합니다.
USkillProjectileCastAction.Settings|이 액션의 투사체 생성 클래스·속도·궤적·조준·차징·소켓 발사·연출 설정입니다. USkillDefinition의 공통 비용·피해 설정과 구분하며 같은 스킬 트리 안에서 액션마다 다르게 구성할 수 있습니다.
UAbilityGrantAndInputManager.HoldAbilityHandlesByInputTag|Press 스킬·그래플처럼 해제가 필요한 능력만 누른 순간의 입력 태그와 핸들로 연결합니다. 선택이 바뀌어도 원래 누른 능력에 해제를 전달합니다.
UAbilityGrantAndInputManager.PendingHoldReleases|키는 놓았지만 아직 해제를 전달하지 못한 능력 핸들입니다. 활성화 전 해제도 기록하고 처리 가능할 때 전달한 뒤 제거합니다.
UAbilityGrantAndInputManager.PendingRemoteActivations|ServerInitiated 활성화 응답을 기다리는 핸들만 기록해 같은 요청의 중복 전송을 막습니다. 로컬 예측 스킬과 ServerOnly 능력은 여기에 보관하지 않습니다.
UStatUpgradeDefinition.AttributeDefaultValues|속성 태그·기본값·투자당 값·우선순위를 보관합니다. CalculateInitialAttributeValues에서 우선순위 순으로 기본값을 합치고 시작 투자분을 같은 투자 공식으로 계산합니다.
UStatUpgradeDefinition.PairedResourceStatTags|최대 자원 태그와 현재 자원 태그를 연결합니다. 초기값 계산에서 현재 자원을 뒤로 정렬하고 기본값이 없는 현재 자원은 실제 최대값으로 채우도록 ASC에 전달합니다.
UBasicAttributeSet.Arcane|신비 수치를 보관합니다. CalculateCooldownDuration이 GetArcane으로 0~100% 감소율을 구해 스킬 기본 쿨다운 시간에 적용합니다.
UBasicAttributeSet.Burn|화상 피해 보너스 수치입니다. GetStatusEffectDamageBonusPercent가 화상 태그일 때 GetBurn으로 읽어 상태 이상 피해 계산에 사용합니다.
UBasicAttributeSet.Frostbite|동상 피해 보너스 수치입니다. GetStatusEffectDamageBonusPercent가 동상 태그일 때 GetFrostbite로 읽습니다.
UBasicAttributeSet.ElectricShock|감전 피해 보너스 수치입니다. GetStatusEffectDamageBonusPercent가 감전 태그일 때 GetElectricShock으로 읽습니다.
UStatusEffectWidget.StackFillDecreaseStartTime|스택 감소 표시를 시작한 시각입니다. NativeTick이 공통 FullStackLifetimeSeconds·StackHoldSeconds 기준으로 게이지를 보간할 때 사용합니다.
UStatusEffectWidget.StackFillDecreaseStartPercent|스택이 마지막으로 갱신됐을 때의 게이지 비율입니다. 시작 시각과 함께 Tick에서 감소하는 화면 비율을 계산합니다.
UStatusEffectWidget.CurrentStackCount|ASC 또는 복제 컴포넌트에서 받은 스택 수를 화면 상태로 보관합니다. 실제 게임 스택은 GAS와 복제 항목에 있으며 이 값은 게이지 표시와 제거 판단에 사용합니다.
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
