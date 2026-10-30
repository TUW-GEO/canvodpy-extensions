"""DAG-parsing test with Airflow.

``apache-airflow`` is a dependency of canvod-airflow, so this test runs in
the workspace; it is skipped where Airflow can't be imported, and on Windows,
where Airflow doesn't run (only POSIX systems; Windows through WSL2).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.platform == "win32":
    pytest.skip("Airflow runs on POSIX systems only", allow_module_level=True)

pytest.importorskip("airflow")

import canvod.airflow


def test_dagbag_imports_cleanly():
    from airflow.models import DagBag

    bag = DagBag(dag_folder=str(Path(canvod.airflow.__file__).parent))
    assert not bag.import_errors, bag.import_errors
    assert "canvod_backfill" in bag.dags


def test_daily_dag_builds_for_a_site():
    from canvod.airflow.daily_processing import create_daily_dag

    tasks = {task.task_id for task in create_daily_dag("FAN", True).tasks}
    assert {"t_wait_for_sp3", "t_process_day", "t_calculate_vod"} <= tasks


def _task_ids(dag) -> set[str]:
    return {task.task_id for task in dag.tasks}


def test_sp3_wait_with_precise_ephemeris_only():
    from canvod.airflow.daily_processing import create_daily_dag

    assert "t_wait_for_sp3" in _task_ids(create_daily_dag("FAN", True))
    assert "t_wait_for_sp3" not in _task_ids(create_daily_dag("FAN", False))


def test_agency_ephemeris_still_works_and_warns():
    from canvod.airflow.daily_processing import create_daily_dag

    with pytest.warns(FutureWarning, match="precise_ephemeris"):
        dag = create_daily_dag("FAN", agency_ephemeris=True)
    assert "t_wait_for_sp3" in _task_ids(dag)
