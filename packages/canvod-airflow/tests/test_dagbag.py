"""DAG-parsing test with Airflow.

``apache-airflow`` is a dependency of canvod-airflow, so this test runs in
the workspace; it is skipped only where Airflow can't be imported.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("airflow")

import canvod.airflow


def test_dagbag_imports_cleanly():
    from airflow.models import DagBag

    bag = DagBag(dag_folder=str(Path(canvod.airflow.__file__).parent))
    assert not bag.import_errors, bag.import_errors
    assert "canvod_backfill" in bag.dags
