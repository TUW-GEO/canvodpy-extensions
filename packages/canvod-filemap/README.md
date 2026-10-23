<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
    <img alt="canVODpy" src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" width="260">
  </picture>
</p>

# canvod-filemap

[![PyPI](https://img.shields.io/pypi/v/canvod-filemap.svg)](https://pypi.org/project/canvod-filemap/)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/TUW-GEO/canvodpy-extensions/blob/main/LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21359005-blue)](https://doi.org/10.5281/zenodo.21359005)

**Naming recipes for receiver files that don't follow the canVOD file name convention.** `canvod-filemap` is one of the
[canVODpy extensions](https://extensions.canvodpy.eu/), optional packages
for [canVODpy](https://canvodpy.eu/), an open Python ecosystem for
GNSS-Transmissometry (GNSS-T) canopy VOD retrievals.

## What it does

`canvodpy run` processes files whose names follow the canVOD convention, in
any folder layout. For a receiver whose files are named differently, a
naming recipe translates each file name to its canonical name, without
renaming any file on disk.

```
{SIT}{T}{NN}{AGC}_R_{YYYY}{DOY}{HHMM}_{PERIOD}_{SAMPLING}_{CONTENT}.{TYPE}
```

Example: `FANA01INK_R_20250010000_15M_05S_AA.rnx`

| Component | Purpose |
|---|---|
| `NamingRecipe` | Translates a receiver's own file names to canonical names |
| `find_recipe`, `create_recipe` | Recipe files at `<config dir>/recipes/<site>/<name>.yaml`; new ones from the template |
| `fetch_recipe`, `check_recipe_url` | Recipes from a raw GitHub link (commit, tag or branch), fetched by every run |

`canvodpy config validate --site <site>` checks before a run which files the
run would process.

## Install

```bash
uv add canvod-filemap
```

canVODpy requires Python 3.14.

## Example

```python
from pathlib import Path

from canvod.filemap import NamingRecipe

recipe = NamingRecipe.load(Path("config/recipes/fangorn/fangorn_reference.yaml"))
vf = recipe.to_virtual_file(Path("rref001a15.25o"))
print(vf.conventional_name)  # canonical canVOD name; the file keeps its name
```

## Documentation

[filemap documentation](https://extensions.canvodpy.eu/packages/filemap/overview/)
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
