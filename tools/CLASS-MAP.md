# Pandora Battle core class atlas

The portfolio embeds `pandora-battle-portfolio/class-map.html`. Nine category
buttons and a ranked selector navigate 100 selected C++ classes. The center is
one UML-like canvas: actual fields and nested struct members live inside each
block, and directed edges show ownership, references and runtime relationships.
A shared class occurs only once within a view.

A block opens that class's canonical graph. Its separate GitHub link opens the
commit-pinned header. The `내용` button and edge clicks open the independent,
initially collapsed detail section below the canvas without changing the graph.
The detail section adds searchable member purposes and source-linked usage lists
while preserving declarations, nested schemas, related data previews and source
evidence. Static `class-index.html` provides
all 100 header links.

`assets/class-graph-model.js` defines compact field compartments, curated hub
views and direct-neighbor views for other core classes. An orthogonal A* router
reserves tracks, avoids node rectangles, and penalizes bends, overlaps and
crossings. Wider canvases use a landscape layout. Pan, zoom, fit, highlighted
relationships and a large view help explore dense views. No CDN or layout
runtime is required. Do not restore the earlier repeated two-block lanes.

The source of selection is `core-class-selection.json`. Class roles and field
meanings are in `core-class-content.py`; semantic runtime/projection edges and
editorial reading paths are in `core-class-flows.py`. Those reading paths remain
source-validation metadata, not separate diagrams in the UI. `cpp-schema.py`
contains the Unreal-aware C++ parsing utilities.

```sh
python -m pip install tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
python tools/build-class-map.py /path/to/Pandora-Battle
node tools/verify-class-map.mjs /path/to/Pandora-Battle
python tools/verify-field-usage.py /path/to/Pandora-Battle
node tools/verify-class-graph.mjs
node --check pandora-battle-portfolio/assets/class-map.js
node --check pandora-battle-portfolio/assets/field-inspector.js
```

The builder requires a clean source checkout and cannot regenerate the previous
576-type map. Priorities express a reading order, not performance. Header
defaults differ from actual `.uasset` values. References are not called ownership
without construction evidence. Dashed projection edges name the intermediary
Widget/Builder; Game Feature ordering is a documented configuration guideline.

Source verification checks all field/schema declarations and source links,
PlayerState ownership, Definition → FSkill → SkillDefinition, Tree growth,
SkillSource registration and AbilitySpec SourceObject use, saved PrimaryAssetIds,
and separation of StateTree and BT. Geometry verification covers all 100 roots
in normal/expanded and portrait/landscape variants: unique connected blocks,
valid fields, source-backed edges, attached ports and no lines through blocks.

Browser verification covers categories, canonical graph navigation/back, search,
independent details, source links, pan/zoom/fit, the large view, mobile and the
portfolio iframe. `?class=APdPlayerState` opens its canonical view; `?wide=1`
opens the large view. `?embed=1` omits standalone chrome and uses a fixed canvas
height to avoid iframe feedback loops. The child reports content height to a
same-origin, exact-source-checked listener in `site.js`. Long detail/index lists
scroll internally so expanded content stays within the parent's height bound.

The main builder also invokes `build-field-usage.py`. It indexes C++ member
references and verified Getter calls using the same pinned source checkout.
`field-usage-content.py` supplies reviewed core-member purposes and reusable
schema descriptions. The index is loaded by `field-inspector.js` only when the
lower details are opened; source revisions must match before it is displayed.

Direct use, external direct use, and one Getter hop have separate lists. Getter
callers include a caller → Getter → member path, definition links, and exact
usage lines. The Getter implementation must itself reference the member; naming
alone is insufficient. Setter-only calls and arbitrary transitive callers are
excluded. Editor/tests and project macro-generated GAS accessors are folded into
separate groups. Comments, strings, shadowing locals, and receivers of unrelated
types are excluded. This is a source index, not a full Unreal compiler: unresolved
dynamic types, Blueprint/reflection uses, and asset values are not inferred.

`verify-field-usage.py` checks every selected member, exact evidence lines and
Getter-to-member definitions, plus regressions for PlayerState, SkillSource,
PandoraDefinition, lexical scope, typed receivers and Setter-only callers.
