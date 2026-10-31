# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-filemap==1.0.0",
#   "marimo>=0.23.9",
# ]
#
# [tool.marimo.opengraph]
# title = "canvod-PACKAGE vX.Y.Z"
# description = "What canvod-PACKAGE vX.Y.Z brings, and how to use it."
# ///

# Template for a release notebook: copy it to
# release-notes/canvod-PACKAGE-vX.Y.Z.py, replace canvod-PACKAGE and X.Y.Z,
# pin the release in the header above ("canvod-filemap==1.1.0", plus
# canvodpy if a cell imports it), and fill in the sections. Delete this
# comment.

import marimo

__generated_with = "0.25.2"
app = marimo.App(
    width="medium",
    app_title="canvod-PACKAGE vX.Y.Z",
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

    # canvod-PACKAGE vX.Y.Z

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-extensions/blob/main/release-notes/canvod-PACKAGE-vX.Y.Z.py)

    Two or three sentences: what the release brings, for whom.

    ```bash
    uv add canvod-PACKAGE==X.Y.Z
    ```

    The full list of changes is in the
    [changelog](https://github.com/TUW-GEO/canvodpy-extensions/blob/canvod-PACKAGE-vX.Y.Z/packages/canvod-PACKAGE/CHANGELOG.md).

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## A new feature

    What it does and when to use it, in the words of the docs. Link the
    docs page that describes it.
    """)
    return


@app.cell
def _():
    # Show the feature with the demo data where it can run here
    # (canvodpy.demo_data()); otherwise show the code or the command in a
    # Markdown cell and say what it needs to run.
    from importlib.metadata import version

    version("canvod-PACKAGE")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Fixes

    - One line per fix that users notice.
    """)
    return


if __name__ == "__main__":
    app.run()
