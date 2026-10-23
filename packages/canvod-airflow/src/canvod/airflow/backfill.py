"""Manual backfill DAG for reprocessing historical GNSS-T data.

Triggered manually with parameters.  Each date in the range becomes an
independent Airflow task instance via dynamic task mapping.
A failure on one date retries that date only — the rest of the batch
continues unaffected.

**Concurrency safety** — Icechunk stores require serialised commits on a
branch.  ``max_active_tis_per_dagrun=1`` enforces this within a single
backfill run.  The ``canvod_store_write`` pool (create it with one slot in
the Airflow UI) provides the same guarantee across simultaneous backfill
runs and the daily DAGs::

    airflow pools set canvod_store_write 1 "Serialise Icechunk commits"

All three parameters are required: the site and the first and last day,
both ``YYYYDDD``. Usage (Airflow UI or CLI)::

    airflow dags trigger canvod_backfill --conf '{
        "site": "fangorn",
        "start_date": "2025001",
        "end_date": "2025010"
    }'
"""

from __future__ import annotations

from datetime import datetime, timedelta

import structlog

from airflow.sdk import Param, dag, task  # type: ignore[unresolved-import]

logger = structlog.get_logger(__name__)


def _task_failure_callback(context):
    """Log structured failure info."""
    ti = context["task_instance"]
    logger.error(
        "BACKFILL TASK FAILED | dag=%s task=%s map_index=%s error=%s",
        ti.dag_id,
        ti.task_id,
        ti.map_index,
        context.get("exception", "unknown"),
    )


@dag(
    dag_id="canvod_backfill",
    schedule=None,  # manual trigger only
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=3,  # allow a few concurrent backfill runs (pool controls writes)
    default_args={
        "owner": "canvod",
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(hours=1),
        "on_failure_callback": _task_failure_callback,
    },
    tags=["canvod", "gnss", "backfill"],
    params={
        # No defaults: a trigger without site and days fails instead of
        # processing a range nobody asked for.
        "site": Param(type="string", description="Site name in the canvodpy settings"),
        "start_date": Param(
            type="string",
            pattern=r"^\d{7}$",
            description="First day, YYYYDDD (e.g. 2025001)",
        ),
        "end_date": Param(
            type="string",
            pattern=r"^\d{7}$",
            description="Last day, YYYYDDD (e.g. 2025010), inclusive",
        ),
    },
    doc_md=__doc__,
)
def canvod_backfill():
    """Process a date range for a single site."""

    @task
    def t_resolve_dates(**context) -> list[str]:
        """Expand start_date..end_date into a list of YYYYDDD strings."""
        import datetime as dt

        from canvod.utils.tools import YYYYDOY

        params = context["params"]
        start = YYYYDOY.from_str(params["start_date"])
        end = YYYYDOY.from_str(params["end_date"])

        if start.date is None:
            raise ValueError(f"Invalid start_date: {params['start_date']!r}")
        if end.date is None:
            raise ValueError(f"Invalid end_date: {params['end_date']!r}")

        dates: list[str] = []
        current = start.date
        while current <= end.date:
            doy = (current - dt.date(current.year, 1, 1)).days + 1
            dates.append(f"{current.year}{doy:03d}")
            current += dt.timedelta(days=1)

        logger.info(
            "backfill: %s — %d days (%s → %s)",
            params["site"],
            len(dates),
            params["start_date"],
            params["end_date"],
        )
        return dates

    @task(
        execution_timeout=timedelta(hours=6),
        # Serialise commits within this DAG run.  One date at a time prevents
        # concurrent Icechunk writes to the same branch.
        max_active_tis_per_dagrun=1,
        # Optional pool for cross-run serialisation (create with slot=1 in UI).
        pool="canvod_store_write",
        pool_slots=1,
    )
    def t_process_day(yyyydoy: str, **context) -> dict:
        """Process the full ingest + VOD pipeline for a single date.

        Idempotent: already-processed dates are skipped by the store's
        three-layer dedup (hash match → temporal overlap → intra-batch).
        """
        from canvodpy.workflows.tasks import (
            calculate_vod,
            check_day,
            process_day,
            validate_ingest,
        )

        site = context["params"]["site"]
        check_day(site, yyyydoy)
        process_day(site, yyyydoy)
        validate_ingest(site, yyyydoy)
        calculate_vod(site, yyyydoy)

        logger.info("backfill: %s %s — ok", site, yyyydoy)
        return {"site": site, "yyyydoy": yyyydoy, "status": "ok"}

    dates = t_resolve_dates()
    t_process_day.expand(yyyydoy=dates)


# Instantiate
canvod_backfill()
