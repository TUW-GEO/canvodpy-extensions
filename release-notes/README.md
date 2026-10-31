# Release notebooks

Every minor and major release of an extension package has a
[marimo](https://marimo.io) notebook here that shows what is new and how to
use it, next to the package's `CHANGELOG.md`. Each pins the release it
describes. Cells run on canVODpy's demo data where they can; others show
code that needs your own data.

| Release | Open |
|---|---|

To write one, copy `_template.py` to `<package>-vX.Y.Z.py`;
[How a release works](https://extensions.canvodpy.eu/releasing/)
says when. CI checks their format (`just check-release-notes`) but doesn't
run them.
