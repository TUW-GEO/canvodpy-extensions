<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
    <img alt="canVODpy" src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" width="260">
  </picture>
</p>

# canvod-adapters

[![PyPI](https://img.shields.io/pypi/v/canvod-adapters.svg)](https://pypi.org/project/canvod-adapters/)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/TUW-GEO/canvodpy-extensions/blob/main/LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21359005-blue)](https://doi.org/10.5281/zenodo.21359005)

**Data exchange between canVODpy and other GNSS-T programs.** `canvod-adapters` is one of the
[canVODpy extensions](https://extensions.canvodpy.eu/), optional packages
for [canVODpy](https://canvodpy.eu/), an open Python ecosystem for
GNSS-Transmissometry (GNSS-T) canopy VOD retrievals.

## What it does

`canvod-adapters` converts observations and VOD between canvodpy and other
programs, in both directions. Every import is checked against canvodpy's
own contract for that data, and every conversion records its provenance
(program, versions, direction, source, time) in the dataset attributes.

| Adapter | Program | Data |
|---|---|---|
| `canvod.adapters.gnssvod` | [gnssvod](https://github.com/vincenthumphrey/gnssvod) (Humphrey et al.) | observations, VOD |

## Install

```bash
uv add canvod-adapters
```

canVODpy requires Python 3.14.

## Example

The example writes into the VOD store of a canvodpy site, so it runs
where canvodpy is installed, as the extensions expect.

```python
from canvod.adapters.gnssvod import GnssvodVod
from canvod.adapters.store import import_vod
from canvodpy import Site

adapter = GnssvodVod(bands={"VOD_L1": ["S1C", "S1W"], "VOD_L2": ["S2W"]}, time_system="GPS")
vod = adapter.import_file("gnssvod_vod.nc")

site = Site("fangorn")
import_vod(adapter, "gnssvod_vod.nc", site.vod_store, "canopy_01_vs_reference_01")
```

## Documentation

[adapters documentation](https://extensions.canvodpy.eu/packages/adapters/overview/)
and the [canVODpy documentation](https://canvodpy.eu/).

## Citation

Please cite the canVODpy extensions with their Zenodo DOI,
[10.5281/zenodo.21359005](https://doi.org/10.5281/zenodo.21359005), and
canVODpy with
[10.5281/zenodo.18496233](https://doi.org/10.5281/zenodo.18496233).

## License

Apache License 2.0. See
[LICENSE](https://github.com/TUW-GEO/canvodpy-extensions/blob/main/LICENSE)
and [NOTICE](https://github.com/TUW-GEO/canvodpy-extensions/blob/main/NOTICE).
