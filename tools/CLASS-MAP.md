# Pandora Battle core class atlas

The portfolio embeds `pandora-battle-portfolio/class-map.html`. It presents 100
selected C++ classes in nine systems. Each system uses small, connected diagrams
with two or three blocks per lane. Repeated blocks refer to the same class; they
make shared dependencies readable without crossing lines. A selected-class view
shows incoming/outgoing connections among the same 100 classes.

Class blocks link to commit-pinned GitHub header declarations. Their separate
data buttons reveal Korean field explanations, actual declarations, nested
struct schemas and previews of referenced class data. Arrows open explanations
with source evidence. Static `class-index.html` provides all 100 header links.

The source of the editorial selection is `core-class-selection.json`. Class
roles and field meanings are in `core-class-content.py`; semantic runtime and
projection relationships and reading lanes are in `core-class-flows.py`.
`cpp-schema.py` contains the Unreal-aware C++ parsing utilities.

```sh
python -m pip install tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
python tools/build-class-map.py /path/to/Pandora-Battle
node tools/verify-class-map.mjs /path/to/Pandora-Battle
node --check pandora-battle-portfolio/assets/class-map.js
```

`build-class-map.py` forwards to `build-core-class-map.py`; it cannot regenerate
the previous 576-type map. Generation requires a clean source checkout. It
checks all selected class definitions, field names, source evidence and per-map
coverage. The generated data also includes direct field/base dependencies among
the selected 100, available in focused view. No plugins, engine classes or
independent struct nodes are added to meet the count.

Priorities are a reading order, not performance measurements. Header defaults
are distinguished from actual `.uasset` values. Field references are not called
ownership without construction evidence. Dashed projection edges explicitly
name the intermediary Widget/Builder; the Game Feature ordering edge represents
a header-documented configuration guideline, not a verified asset sequence.

Key regression checks cover PlayerState ownership, Definition → FSkill →
SkillDefinition, Tree growth state, SkillSource registration and AbilitySpec
SourceObject use, saved PrimaryAssetIds, and separation of StateTree and BT.
Field/schema declarations and every source link are checked against the pinned
checkout. All categories must include every one of their selected classes.

Browser verification covers the embedded and standalone routes, system selection,
search (class/field/Korean description), empty results, data/reference drill-down,
nested schemas, arrow explanations, incoming/outgoing views, real header-link
navigation, and desktop/mobile overflow. The viewer uses plain DOM/CSS arrows
without a CDN or external layout runtime. `?class=APdPlayerState` opens focused
view; `?embed=1` omits standalone chrome. The iframe reports its height to a
same-origin, exact-source-checked listener in `site.js`.
