<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
    <img alt="canVODpy" src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" width="260">
  </picture>
</p>

# canvod-airflow

[![PyPI](https://img.shields.io/pypi/v/canvod-airflow.svg)](https://pypi.org/project/canvod-airflow/)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/TUW-GEO/canvodpy-extensions/blob/main/LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21359005-blue)](https://doi.org/10.5281/zenodo.21359005)

**Apache Airflow DAGs that run the canVODpy pipeline every day.** `canvod-airflow` is one of the
[canVODpy extensions](https://extensions.canvodpy.eu/), optional packages
for [canVODpy](https://canvodpy.eu/), an open Python ecosystem for
GNSS-Transmissometry (GNSS-T) canopy VOD retrievals.

## What it does

`canvod-airflow` wraps the task functions of `canvodpy run`
(`canvodpy.workflows.tasks`) into Airflow TaskFlow DAGs. No pipeline logic
lives here: every task calls `canvodpy.workflows.tasks`, which has no
Airflow dependency of its own.

| DAG | Trigger | Tasks |
|---|---|---|
| `canvod_{site}` | `@daily` | `t_validate_dirs → t_wait_for_data (→ t_wait_for_sp3) → t_process_day → t_validate_ingest → t_calculate_vod` |
| `canvod_backfill` | manual (params `site`, `start_date`, `end_date`) | `t_resolve_dates → t_process_day`, one mapped task per day |

There is one daily DAG per site of the canvodpy settings, created when
Airflow parses the DAG file. `t_wait_for_sp3` runs only when the settings use
agency orbit and clock products instead of broadcast ephemerides.

## Install

```bash
uv add canvod-airflow
```

This installs `apache-airflow>=3.0` too; an Airflow 3 that is already
installed is used as it is. canVODpy requires Python 3.14.
Airflow runs on POSIX systems (Linux, macOS); on Windows, run it in WSL2
([Airflow's prerequisites](https://airflow.apache.org/docs/apache-airflow/stable/installation/prerequisites.html)).

## Deployment

Point Airflow's `dags_folder` at a module that imports both DAG modules
(Airflow only parses files that contain the words "airflow" and "dag"):

```python
# <dags_folder>/canvod_dags.py
from canvod.airflow.daily_processing import *  # noqa: F403  (airflow dag)
from canvod.airflow.backfill import *  # noqa: F403
```

Create the `canvod_store_write` pool with one slot. Every task that writes
to a store (`t_process_day`, `t_calculate_vod`) runs in it, so commits to an
Icechunk store happen one at a time across all DAGs and backfill runs:

```bash
airflow pools set canvod_store_write 1 "Serialize Icechunk commits"
```

## Documentation

[airflow documentation](https://extensions.canvodpy.eu/packages/airflow/overview/)
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
