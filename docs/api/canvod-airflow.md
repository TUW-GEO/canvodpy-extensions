# `canvod.airflow` API reference

## Package

::: canvod.airflow

!!! note "The DAG modules are documented by hand"
    `daily_processing.py` and `backfill.py` import `airflow` at module
    level, which is required to build the TaskFlow DAGs, so mkdocstrings
    cannot import them in an environment without Airflow. Their public
    interface is described below by hand instead.

## `daily_processing`

One factory builds the daily DAG of a site. Importing the module builds
one DAG for every site in canvodpy's settings file.

### `create_daily_dag(site_name: str, precise_ephemeris: bool)`

Builds the daily DAG of `site_name`, scheduled daily. Chain:
`validate_dirs → wait_for_data → (wait_for_sp3) → process_day → validate_ingest → calculate_vod`.

When `precise_ephemeris` is true, the DAG also waits for the SP3/CLK
products before it processes the day. `agency_ephemeris`, its old name,
works until the next major version and warns.

## `backfill`

### `canvod_backfill`

A manually triggered DAG that accepts `site`, `start_date`, and `end_date`
(`YYYYDDD` format) as Airflow parameters. It expands the date range into
one `t_process_day` task per date. The tasks run with
`max_active_tis_per_dagrun=1`.

See the [Overview](../packages/airflow/overview.md) for the usage
examples.
