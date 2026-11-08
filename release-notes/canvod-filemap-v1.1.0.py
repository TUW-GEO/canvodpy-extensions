# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-filemap==1.1.0",
#   "marimo>=0.23.9",
# ]
#
# [tool.marimo.opengraph]
# title = "canvod-filemap v1.1.0"
# description = "What canvod-filemap v1.1.0 brings, and how to use it."
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(
    width="medium",
    app_title="canvod-filemap v1.1.0",
)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    <p align="center">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
        <img src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" alt="canVODpy logo" width="280">
      </picture>
    </p>

    # canvod-filemap v1.1.0

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-extensions/blob/main/release-notes/canvod-filemap-v1.1.0.py)

    Naming recipes now map RINEX navigation files too, so a receiver's
    own navigation file names work with canvodpy's broadcast ephemeris
    without renaming the files.

    ```bash
    uv add canvod-filemap==1.1.0
    ```

    The full list of changes is in the
    [changelog](https://github.com/TUW-GEO/canvodpy-extensions/blob/canvod-filemap-v1.1.0/packages/canvod-filemap/CHANGELOG.md).

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Naming recipes for RINEX navigation files

    With `ephemeris_source: broadcast`, canvodpy takes the satellite
    positions from the receiver's RINEX navigation files. They need
    canonical names of type `nav` with sampling `00U` (unspecified, as in
    RINEX file names), for example `FANA01INK_R_20250010000_15M_00U_AA.nav`.
    A recipe now gives them these names: set `file_type: nav` and
    `sampling: "00U"`. The rest works as for observation files.

    A recipe that pairs `nav` with a sampling interval, or `00U` with
    another file type, is refused when it loads.

    The recipe below maps the 15-minute navigation files of a canopy
    receiver, named like `ract001a00.25p`:
    """)
    return


@app.cell
def _():
    from pathlib import Path

    from canvod.filemap.recipe import NamingRecipe

    nav_recipe = NamingRecipe.from_yaml("""
    name: fangorn_canopy_nav
    site: FAN
    agency: INK
    receiver_number: 1
    receiver_type: canopy
    sampling: "00U"
    period: "15M"
    file_type: nav
    glob: "*.??p"
    fields:
      - skip: 4
      - doy: 3
      - hour_letter: 1
      - minute: 2
      - skip: 1
      - yy: 2
      - skip: 1
    """)

    {
        _name: nav_recipe.to_virtual_file(Path(_name)).canonical_str
        for _name in ["ract001a00.25p", "ract001a15.25p", "ract001x45.25p"]
    }
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Use it in canvodpy

    Save the recipe as `recipes/<site>/<name>.yaml` in canvodpy's settings
    folder, or give its raw GitHub URL, and name it in the receiver's
    `nav_recipe` setting, next to `nav_directory`:

    ```yaml
    sites:
      fangorn:
        receivers:
          canopy_01:
            nav_directory: canopy_01_nav
            nav_recipe: fangorn_canopy_nav
    ```

    More: [Naming recipes](https://extensions.canvodpy.eu/packages/filemap/overview/)
    and canvodpy's
    [ephemeris sources](https://canvodpy.eu/packages/readers/ephemeris-sources/).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Fixes

    - **Deeply nested recipes:** a recipe file nested deeper than Python
      can read raised `RecursionError`, and a recipe fetched from a URL
      ended the run with a traceback. It is now refused as "not a YAML
      file: the YAML is nested too deeply to read"
      ([#134](https://github.com/TUW-GEO/canvodpy-extensions/pull/134)).
    """)
    return


if __name__ == "__main__":
    app.run()
