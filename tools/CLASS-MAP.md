# Pandora Battle core class atlas

The portfolio embeds `pandora-battle-portfolio/class-map.html`. Nine category
buttons and a ranked selector navigate 100 selected C++ classes. The center is
one UML-like canvas: actual fields and nested struct members live inside each
block, and directed edges show ownership, references and runtime relationships.
A shared class occurs only once within a view.

A block opens that class's canonical graph. Its separate GitHub link opens the
commit-pinned header. The `내용` button and edge clicks open the independent,
initially collapsed detail section below the canvas without changing the graph.
The detail section preserves Korean explanations, declarations, nested schemas,
related data previews and source evidence. Static `class-index.html` provides
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
node tools/verify-class-graph.mjs
node --check pandora-battle-portfolio/assets/class-map.js
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
