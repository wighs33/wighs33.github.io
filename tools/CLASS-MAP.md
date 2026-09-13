# Pandora Battle class atlas

The portfolio embeds `pandora-battle-portfolio/class-map.html`. The viewer uses
native SVG and a generated static JavaScript data file, with no CDN dependency.
`class-index.html` provides all source links without JavaScript.

To update the source snapshot, use a clean checkout of the public
`wighs33/Pandora-Battle` repository containing `Source` and the plugin sources:

```sh
python -m pip install tree-sitter==0.25.2 tree-sitter-cpp==0.23.4
python tools/build-class-map.py /path/to/Pandora-Battle
node tools/verify-class-map.mjs /path/to/Pandora-Battle
```

Also update the two summary counts in the portfolio homepage's `#classes`
section if the source counts changed. No Unreal build or engine installation is
needed. Source URLs use the analyzed commit and declaration line so links remain
consistent with the displayed graph.

The parser collects named class/struct definitions from tracked C++ headers and
implementation files. It masks Unreal annotation macros, comments and conditional
directives while retaining source offsets. An independent lexical inventory
checks for missing definitions; unresolved parser errors and ambiguous type
references stop generation. Blueprint asset dependencies, macro-generated types,
engine definitions, runtime calls and ownership are outside the graph's scope.
Conditional branches are analyzed together. Implementation-local named types
link to `.cpp`; all other nodes link to their headers.

Edges represent internal inheritance, member field types, or explicit function
signature/alias types. Inline method bodies, comments, forward declarations and
include directives do not create relationship edges. Third-party plugin types
are explicitly tagged and filterable.

Browser checks: initial focus, all-node view including isolated types, search by
name/path, empty results, origin/group/kind/direction filters, relation toggles,
source-link navigation, keyboard pan/zoom, desktop/mobile layout and iframe
height. The viewer can be opened with `?view=all` or `?class=APdPlayerState`;
`?embed=1` removes the standalone page heading.
