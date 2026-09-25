"""Reviewed current responsibilities where the previous core atlas became stale."""
NOTES = {
 'UPandoraSkillSource':dict(role='판도라 스킬 출처',purpose='PandoraComponent가 소유·복제하는 출처 객체입니다. 판도라 정의·스킬 인덱스·로드아웃 방향 세 값으로 실제 스킬을 조회하며, 해당 출처가 붙은 ASC 활성 효과에서 남은 쿨다운을 읽습니다.'),
 'UPdAbilitySystemComponent':dict(role='GAS 실행과 속성 적용',purpose='속성 초기화·변경과 능력 실행을 연결하며 입력은 AbilityGrantAndInputManager에 전달합니다. 능력 목록 변경과 제거 이벤트를 알립니다. 판도라 출처 객체의 보관·복제는 PandoraComponent가 담당합니다.'),
 'UPandoraComponent':dict(role='판도라 보유·선택과 스킬 출처 소유',purpose='정의 기반 보유 목록, 방향별 로드아웃과 능력 핸들을 관리합니다. OwnedSkillSources로 출처 객체를 보관·복제하고 ASC의 능력 제거 이벤트에 맞춰 정리합니다.'),
 'UAbilityGrantAndInputManager':dict(role='능력 입력 전달',purpose='누름을 즉시 전달하고 Press·그래플처럼 입력 해제를 사용하는 능력만 HoldAbilityHandlesByInputTag에 보관합니다. 별도의 원격 활성화·입력 해제 대기 목록은 없습니다.'),
 'USkillAbility':dict(role='액션 트리 실행과 판도라 출처 해석',purpose='SkillDefinition의 Action 트리를 시전별로 복제해 실행합니다. 판도라 출처에서 스킬·방향·레벨을 해석하고 입력, 지속시간, 비용 확정과 종료 시 쿨다운을 관리합니다.'),
 'UPdGameplayAbility':dict(role='공통 능력 실행',purpose='피해·상태 효과 Spec, 이동 제어, 조준 작업과 연출을 공통 API로 제공합니다. 판도라별 출처 해석과 슬롯 피해 보정은 USkillAbility가 담당합니다.'),
 'FPandoraSkillBinder':dict(role='판도라 스킬 부여와 입력 연결',purpose='SourceOwner인 PandoraComponent를 통해 스킬 출처를 만들고 ASC에 공통 SkillAbility를 부여합니다. 이미 부여된 스킬은 재사용하며 선택에 따른 입력 연결만 갱신합니다.'),
 'AWeaponBase':dict(role='공통 무기 표현과 공격 진입점',purpose='아이템 정의와 소켓·몽타주·스킬 트레일 표현을 공유합니다. 근접 판정은 AMeleeWeapon, 발사체 생성과 원거리 공격은 ARangedWeaponBase가 담당합니다.'),
 'AMeleeWeapon':dict(role='근접 무기 판정과 참격',purpose='AWeaponBase의 공통 표현을 사용하며 근접 피해 판정, 충돌 범위와 참격 처리를 담당합니다.'),
 'ARangedWeaponBase':dict(role='원거리 무기 발사',purpose='발사체 생성·발사와 원거리 피해 처리를 공통화합니다. ABow와 AGun이 이를 상속합니다.'),
 'UPaintCanvasComponent':dict(role='페인트 캔버스 상태·복제',purpose='캔버스의 스트로크·브러시·입력 상태와 서버 검증·복제를 관리합니다. 실제 표시 갱신은 PaintCanvasDisplay에 연결합니다.'),
}
