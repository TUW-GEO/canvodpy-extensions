"""Airflow DAG for GNSS-Transmissometry daily processing.

One DAG per configured site (``canvod_{site}``)::

    validate_dirs → wait_for_data (→ wait_for_sp3)
      → process_day → validate_ingest → calculate_vod

``process_day`` and ``calculate_vod`` run the code of ``canvodpy run``
(``canvodpy.workflows.tasks``): each receiver is read in the
``reader_format`` of its site configuration, with the ephemeris source of
``processing.params.ephemeris_source``. With agency ephemerides the DAG
also waits for the SP3/CLK products (12-18 days for final products).

Requirements
------------
* ``canvodpy`` installed in the Airflow worker environment.
* Apache Airflow >= 3.0 (a dependency of canvod-airflow).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import structlog

from airflow.sdk import dag, task  # type: ignore[unresolved-import]

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration helpers (parse-time safe)
# ---------------------------------------------------------------------------


def _get_configured_sites() -> dict:
    """Return {site_name: site_cfg} from canvodpy config.

    Imports are deferred so that the DAG file can be parsed by the Airflow
    scheduler even when ``canvodpy`` is unavailable (parse-time safety).
    """
    try:
        from canvod.config import load_config

        return dict(load_config().sites.sites)
    except Exception:
        logger.warning("Could not load canvodpy config — no DAGs generated")
        return {}


def _uses_agency_ephemeris() -> bool:
    """Whether runs use agency SP3/CLK products (``ephemeris_source``)."""
    from canvod.config import load_config

    return load_config().processing.params.ephemeris_source != "broadcast"


def _run_date(ds: str | None) -> str:
    """The ``ds`` Airflow passes to a running task (``YYYY-MM-DD``).

    Tasks declare ``ds`` with the default ``None``, the only default
    Airflow 3 allows for a context key; it fills in the value at run time.
    """
    if ds is None:
        msg = "Airflow passes ds to a running task; this task got none"
        raise ValueError(msg)
    return ds


def _ds_to_yyyydoy(ds: str | None) -> str:
    """Convert Airflow ``ds`` (``YYYY-MM-DD``) to ``YYYYDDD``."""
    import datetime as dt

    date = dt.date.fromisoformat(_run_date(ds))
    doy = (date - dt.date(date.year, 1, 1)).days + 1
    return f"{date.year}{doy:03d}"


# ---------------------------------------------------------------------------
# Failure callback
# ---------------------------------------------------------------------------


def _task_failure_callback(context):
    """Log structured failure info. Future: Slack/email hook."""
    ti = context["task_instance"]
    logger.error(
        "TASK FAILED | dag=%s task=%s date=%s error=%s log_url=%s",
        ti.dag_id,
        ti.task_id,
        context.get("ds", "?"),
        context.get("exception", "unknown"),
        ti.log_url,
    )


# ---------------------------------------------------------------------------
# Shared default_args
# ---------------------------------------------------------------------------

_DEFAULT_ARGS = {
    "owner": "canvod",
    "retries": 5,
    "retry_delay": timedelta(minutes=30),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(hours=12),
    "execution_timeout": timedelta(hours=2),
    "on_failure_callback": _task_failure_callback,
}

_START_DATE = datetime(2025, 1, 1)


# ---------------------------------------------------------------------------
# Daily DAG
# ---------------------------------------------------------------------------


def create_daily_dag(site_name: str, agency_ephemeris: bool):
    """Create the daily processing DAG for *site_name*.

    Parameters
    ----------
    site_name : str
        Site name in the canvodpy configuration.
    agency_ephemeris : bool
        Whether runs use agency SP3/CLK products; the DAG then waits for
        them before processing.
    """

    @dag(
        dag_id=f"canvod_{site_name}",
        schedule="@daily",
        start_date=_START_DATE,
        catchup=False,
        max_active_runs=1,
        default_args=_DEFAULT_ARGS,
        tags=["canvod", "gnss", site_name],
        doc_md=__doc__,
    )
    def daily_dag():
        @task(retries=0)
        def t_validate_dirs(ds: str | None = None) -> dict:
            from canvodpy.workflows.tasks import validate_data_dirs

            return validate_data_dirs(site_name)

        @task.sensor(
            poke_interval=3600,
            timeout=3600 * 24 * 21,
            mode="reschedule",
        )
        def t_wait_for_data(
            valid_info: dict,
            ds: str | None = None,
        ):
            """Wait until every receiver has files for the day (up to 21 days)."""
            from canvodpy.workflows.tasks import check_day

            from airflow.sdk import (
                PokeReturnValue,  # type: ignore[unresolved-import]
            )

            _ = valid_info
            try:
                result = check_day(site_name, _ds_to_yyyydoy(ds))
            except RuntimeError:
                return PokeReturnValue(is_done=False)
            return PokeReturnValue(is_done=True, xcom_value=result)

        @task.sensor(
            poke_interval=3600 * 6,
            timeout=3600 * 24 * 21,
            mode="reschedule",
        )
        def t_wait_for_sp3(
            data_info: dict,
            ds: str | None = None,
        ):
            """Wait for SP3/CLK products (date-age heuristic, up to 21 days)."""
            from canvodpy.workflows.tasks import check_sp3_availability

            _ = data_info
            return check_sp3_availability(_run_date(ds))

        @task(
            execution_timeout=timedelta(hours=4),
            pool="canvod_store_write",
            pool_slots=1,
        )
        def t_process_day(
            ready_info: dict,
            ds: str | None = None,
        ) -> dict:
            from canvodpy.workflows.tasks import process_day

            _ = ready_info
            return process_day(site_name, _ds_to_yyyydoy(ds))

        @task(execution_timeout=timedelta(hours=1))
        def t_validate_ingest(
            process_info: dict,
            ds: str | None = None,
        ) -> dict:
            from canvodpy.workflows.tasks import validate_ingest

            _ = process_info
            return validate_ingest(site_name, _ds_to_yyyydoy(ds))

        @task(
            execution_timeout=timedelta(hours=1),
            pool="canvod_store_write",
            pool_slots=1,
        )
        def t_calculate_vod(
            ingest_valid: dict,
            ds: str | None = None,
        ) -> dict:
            from canvodpy.workflows.tasks import calculate_vod

            _ = ingest_valid
            return calculate_vod(site_name, _ds_to_yyyydoy(ds))

        # Calling a task in the DAG body passes an XComArg, which Airflow
        # resolves to the upstream task's return value at run time. The
        # airflow.sdk type hints expect the resolved type, hence the ignores.
        valid_info = t_validate_dirs()
        ready_info = t_wait_for_data(valid_info=valid_info)  # ty: ignore[invalid-argument-type]
        if agency_ephemeris:
            ready_info = t_wait_for_sp3(data_info=ready_info)  # ty: ignore[invalid-argument-type]
        process_info = t_process_day(ready_info=ready_info)  # ty: ignore[invalid-argument-type]
        ingest_valid = t_validate_ingest(process_info=process_info)  # ty: ignore[invalid-argument-type]
        t_calculate_vod(ingest_valid=ingest_valid)  # ty: ignore[invalid-argument-type]

    return daily_dag()


# ---------------------------------------------------------------------------
# Dynamic DAG generation: one DAG per configured site
# ---------------------------------------------------------------------------

_SITES = _get_configured_sites()
if _SITES:
    _AGENCY_EPHEMERIS = _uses_agency_ephemeris()
    for _site_name in _SITES:
        globals()[f"canvod_{_site_name}"] = create_daily_dag(_site_name, _AGENCY_EPHEMERIS)
