# Release notebooks

Every minor and major release of an extension package has a
[marimo](https://marimo.io) notebook here that shows what is new and how to
use it, next to the package's `CHANGELOG.md`. Each pins the release it
describes. Cells run on canVODpy's demo data where they can; others show
code that needs your own data.

| Release | Open |
|---|---|
| [canvod-filemap v1.1.0](canvod-filemap-v1.1.0.py): naming recipes for RINEX navigation files | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-extensions/blob/main/release-notes/canvod-filemap-v1.1.0.py) |
| [canvod-airflow v1.1.0](canvod-airflow-v1.1.0.py): the SP3/CLK wait in canvod-airflow, Airflow 3 fix | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-extensions/blob/main/release-notes/canvod-airflow-v1.1.0.py) |

To write one, copy `_template.py` to `<package>-vX.Y.Z.py`;
[How a release works](https://extensions.canvodpy.eu/releasing/)
says when. CI checks their format (`just check-release-notes`) but doesn't
run them.
