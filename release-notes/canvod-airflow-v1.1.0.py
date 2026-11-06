# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "canvod-airflow==1.1.0",
#   "marimo>=0.23.9",
# ]
#
# [tool.marimo.opengraph]
# title = "canvod-airflow v1.1.0"
# description = "What canvod-airflow v1.1.0 brings, and how to use it."
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(
    width="medium",
    app_title="canvod-airflow v1.1.0",
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

    # canvod-airflow v1.1.0

    [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/TUW-GEO/canvodpy-extensions/blob/main/release-notes/canvod-airflow-v1.1.0.py)

    The daily DAG builds with Airflow 3 again, and the wait for the SP3/CLK
    products now lives in canvod-airflow: canvodpy v1.1.0 deprecates its
    own copy. The DAG follows canvodpy's new name for the SP3/CLK
    products, the precise ephemeris.

    ```bash
    uv add canvod-airflow==1.1.0
    ```

    The full list of changes is in the
    [changelog](https://github.com/TUW-GEO/canvodpy-extensions/blob/canvod-airflow-v1.1.0/packages/canvod-airflow/CHANGELOG.md).

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## The SP3/CLK wait is part of canvod-airflow

    `check_sp3_availability`, which decides when the daily DAG stops
    waiting for the SP3/CLK products of a day, is now
    `canvod.airflow.sensors.check_sp3_availability`. The DAG calls it from
    there. It goes by the day's age: it continues after 2 days for `rapid`
    and 14 days for `final` products (`processing.aux_data.product_type`),
    and skips days older than 30 days, as before.

    canvodpy v1.1.0 deprecates `canvodpy.workflows.tasks.check_sp3_availability`,
    the only function in canvodpy that needed Airflow. A DAG of your own
    that calls it changes one import:

    ```python
    # before
    from canvodpy.workflows.tasks import check_sp3_availability
    # now
    from canvod.airflow.sensors import check_sp3_availability
    ```

    More: [canvod-airflow](https://extensions.canvodpy.eu/packages/airflow/overview/#how-it-fits-into-a-run).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## `agency_ephemeris` is now called `precise_ephemeris`

    canvodpy calls the SP3/CLK products of an analysis center the precise
    ephemeris (`ephemeris_source: precise`). `create_daily_dag()` follows:
    its argument is `precise_ephemeris`, which adds the wait for the
    SP3/CLK products. `agency_ephemeris` still works until the next major
    version and warns:

    ```python
    from canvod.airflow.daily_processing import create_daily_dag

    dag = create_daily_dag("fangorn", precise_ephemeris=True)
    ```

    The DAGs that canvod-airflow builds for the sites of the settings file
    choose it from `processing.params.ephemeris_source`, as before.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Fixes

    - **Airflow 3:** `create_daily_dag()` raised for every site, since
      Airflow 3 allows only `None` as the default of `ds`. The tasks now
      take `ds` from the running task
      ([#111](https://github.com/TUW-GEO/canvodpy-extensions/issues/111)).
    """)
    return


if __name__ == "__main__":
    app.run()
