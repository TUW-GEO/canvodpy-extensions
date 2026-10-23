# canvod-airflow

`canvod-airflow` turns canvodpy's task functions into Airflow DAGs. One
daily DAG per site runs the site's processing, and one backfill DAG
covers a date range. Every task calls `canvodpy.workflows.tasks`, so no
pipeline logic lives here.

## When you need it

You need it when a site's processing runs on a schedule you don't want to
start by hand, or when you want to reprocess a date range you already
ran. You don't need it when you run `canvodpy run` yourself, or when you
process one batch once.

## Install

```bash
uv add canvod-airflow
```

This also installs `apache-airflow>=3.0`; an Airflow 3 that is already
installed is used as it is.

## A minimal example

Point a `dags_folder` at a shim module that imports both DAG modules, so
Airflow's DagBag finds them. Airflow's pre-filter scans the folder for
DAG files. Give the shim a name that holds the keywords, for example
`canvod_dags.py`:

```python
# <dags_folder>/canvod_dags.py
from canvod.airflow.daily_processing import *  # noqa: F403  (Airflow DAG scan)
from canvod.airflow.backfill import *  # noqa: F403
```

Importing the module builds the DAGs. For each site in
canvodpy's settings file, the package builds a daily DAG named
`canvod_{site}`:

```
t_validate_dirs → t_wait_for_data → (t_wait_for_sp3) → t_process_day → t_validate_ingest → t_calculate_vod
```

`t_validate_dirs` checks the receiver directories. `t_wait_for_data` and
`t_wait_for_sp3` are sensors: they wait until the files of the receiver and
the satellite products are there, holding up to 21 days. `t_process_day`
reads the files and stores the observations, `t_validate_ingest` checks
them, and `t_calculate_vod` computes the VOD.

To reprocess a date range, trigger `canvod_backfill` by hand with the site
and the range:

```bash
airflow dags trigger canvod_backfill --conf '{
    "site": "Rosalia",
    "start_date": "2025-001",
    "end_date": "2025-010"
}'
```

Each date becomes one mapped task. A failure on one date retries only
that date; the rest of the range continues.

## How it fits into a run

The tasks call canvodpy's task functions directly: `validate_data_dirs`,
`check_day`, `check_sp3_availability`, `process_day`, `validate_ingest`,
and `calculate_vod`. These functions are stateless and accept only
primitives, so they carry dates and settings to and from Airflow. Use
them in a script or a notebook without Airflow if you want.

The daily DAG waits for SP3/CLK products only when a run uses agency
ephemerides, that is when `processing.params.ephemeris_source` is not
`broadcast`. With `broadcast`, the satellite angles come from the SBF
files themselves and the results are available the same day. See
[Configuration](https://canvodpy.eu/guides/configuration/), and for how
the runs scale and write, [Parallel
processing](https://canvodpy.eu/guides/parallel-processing/) and
[Icechunk stores](https://canvodpy.eu/packages/store/icechunk/).

## Limits and known issues

- An Icechunk store takes one commit at a time. Every task that writes to
  a store uses the pool `canvod_store_write` with one slot, which
  serializes the writes across the DAGs and the backfill runs. Create the
  pool once:
  ```bash
  airflow pools set canvod_store_write 1 "Serialise Icechunk commits"
  ```
- Within one backfill run, the dates process one at a time
  (`max_active_tis_per_dagrun=1`).
- The settings file must be reachable from the Airflow worker. If it is
  not, no DAGs are generated.

## API

See the [API reference](../../api/canvod-airflow.md) for the full public
API.
