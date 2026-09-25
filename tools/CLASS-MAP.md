# Pandora Battle complete class tree

The portfolio embeds `pandora-battle-portfolio/class-map.html`. The previous
100-class UML canvas and selection criteria have been removed. The source
browser includes every class/struct definition in `Source/LabProject/**/*.h`,
plus named enum and helper namespace declarations. Implementation-local types
in `.cpp`, editor-module types, and third-party/engine source are outside this
published header index. C++ usage is scanned across the project's Source files.

The September 25 revision pins `36e83199333f44de7e5f836c02b6ad731f63eb2a`:
322 classes, 205 structs, 19 namespaces, 33 enums, 4,421 members and 5,968
declared functions across 358 headers. Counts are generated, not a limit.

## Navigation

- Folder view uses actual paths. Inside a folder, same-folder derived classes
  appear beneath their parent. Cross-folder bases remain explicit row labels.
- Inheritance view ignores folders and shows the first direct base as a tree
  parent. All direct bases, including interfaces, are listed in the details.
  Template arguments never become additional parents.
- Classes and other declarations have separate type badges. Data/helper groups
  can be expanded; search covers names, paths, members and function names.
- Clicking a name opens its details below the tree. The separate GitHub link
  opens its commit-pinned declaration. Search remains intact when a selection
  changes. Back-to-tree, history, type filters and expand/collapse are supported.
- Details contain the source summary, every declared member, purpose, direct
  uses and verified Getter callers, function declarations/comments, inheritance
  and member-type connections. Empty classes still have function/source details.
- The tree and detail lists scroll internally. Embedded height messages retain
  the same-origin, exact-source check in `site.js` and remain within its bound.

## Corrections to the supplied outline

The supplied outline is a starting point, not declaration evidence. Latest
source headers determine names, kinds, locations and direct inheritance.

| Supplied entry | Verified representation |
| --- | --- |
| `UPandoraSkillBinder` | `FPandoraSkillBinder`, a C++ class |
| `USkillActions` | File containing Wait/Event/Montage/Dash/Effect/Area/Spawn/Projectile/Repeat action classes |
| `ASword` directly under `AWeaponBase` | `AMeleeWeapon`; `ARangedWeaponBase` is the base of `ABow` and `AGun` |
| `FStateTree_PdUtilityTasks` and similar file names | Actual task/condition structs declared inside those headers |
| `FCharacterHitValidation`, `UTargetValidator` | `PdCharacterHitValidation`, `PdTargetValidator` namespaces |
| `ASkillGroundProjection` | `PdSkillGroundProjection` namespace and `FGroundProjectionResult` |
| `UWidgetContentBundle` | `EWidgetContentBundle` / `EWidgetContentBundleState` enums |
| `UItemViewData`, `UFilterButtonHighlight` | `FItemViewData`, `FItemViewDataBuilder`, `FFilterButtonHighlightState` |
| `UPandoraLoadoutUiModel` | `FPandoraLoadoutUiModel` |
| Engine base names | Non-project inheritance nodes, not invented project classes |

The new revision also moves source ownership/replication from ASC to
`UPandoraComponent.OwnedSkillSources`; source data now has three fields, with
the old PandoraLevel field removed. Skill-specific source resolution is in
`USkillAbility`. Reviewed explanations are updated accordingly.

## Rebuild and verification

```sh
python -m pip install tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
python tools/build-class-map.py /path/to/Pandora-Battle
python tools/verify-class-tree.py /path/to/Pandora-Battle
python tools/verify-field-usage.py /path/to/Pandora-Battle
node tools/verify-class-tree.mjs
node --check pandora-battle-portfolio/assets/class-map.js
node --check pandora-battle-portfolio/assets/field-inspector.js
```

`build-class-tree.py` discovers declarations, fields and methods; it has no
selected-class list. An independent declaration scan verifies coverage. Source
verification checks exact declarations/lines, updated weapon bases and source
ownership, while model verification checks unique placement for every declaration
and every type filter. `core-class-content.py` supplies existing reviewed roles;
`class-tree-content.py` overrides changed responsibilities. Header documentation
supplies additional summaries, with explicit declaration-based summaries when
no narrative is present.

`build-field-usage.py` indexes typed C++ receivers and one verified Getter hop.
Setter-only calls and arbitrary transitive callers are excluded. Member usage
bodies render when expanded to keep large classes responsive. Source evidence,
lexical scope fixtures, and Getter/member paths are verified. Blueprint uses,
dynamic receivers and actual asset values are not inferred. Website validation
does not compile the Unreal project.
