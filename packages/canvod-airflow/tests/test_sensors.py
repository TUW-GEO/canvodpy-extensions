"""Tests of the SP3/CLK sensor gate.

Expected ages come from the product latencies: rapid products after 2
days, final products after 14 days. Skipped on Windows, where Airflow
doesn't run (only POSIX systems; Windows through WSL2).
"""

from __future__ import annotations

import datetime as dt
import sys
from types import SimpleNamespace

import pytest

if sys.platform == "win32":
    pytest.skip("Airflow runs on POSIX systems only", allow_module_level=True)

import canvod.config
from airflow.sdk.exceptions import (
    AirflowSkipException,  # type: ignore[unresolved-import]
)
from canvod.airflow.sensors import check_sp3_availability

TODAY = dt.date(2025, 3, 1)


def _ds(age_days: int) -> str:
    return (TODAY - dt.timedelta(days=age_days)).isoformat()


@pytest.fixture
def product_type(monkeypatch):
    """Set ``processing.aux_data.product_type`` of the loaded settings."""

    def _set(value: str) -> None:
        settings = SimpleNamespace(
            processing=SimpleNamespace(aux_data=SimpleNamespace(product_type=value))
        )
        monkeypatch.setattr(canvod.config, "load_config", lambda: settings)

    return _set


@pytest.mark.parametrize(
    ("kind", "age", "ready"),
    [
        ("rapid", 1, False),
        ("rapid", 2, True),
        ("final", 13, False),
        ("final", 14, True),
    ],
)
def test_gate_per_product_type(product_type, kind, age, ready):
    product_type(kind)
    result = check_sp3_availability(_ds(age), today=TODAY)
    assert result.is_done is ready
    assert result.xcom_value == {
        "sp3_ready": ready,
        "product_type": kind,
        "age_days": age,
        "min_age_days": 2 if kind == "rapid" else 14,
    }


def test_falls_back_to_final_when_settings_fail(monkeypatch):
    def _broken():
        raise RuntimeError("no settings")

    monkeypatch.setattr(canvod.config, "load_config", _broken)
    result = check_sp3_availability(_ds(13), today=TODAY)
    assert result.is_done is False
    assert result.xcom_value == {
        "sp3_ready": False,
        "product_type": "final",
        "age_days": 13,
        "min_age_days": 14,
    }


def test_skips_days_older_than_30_days_on_catchup(product_type):
    """Only catchup or old ``ds`` runs get here: the sensor times out after 21 days."""
    product_type("final")
    assert check_sp3_availability(_ds(30), today=TODAY).is_done is True
    with pytest.raises(AirflowSkipException):
        check_sp3_availability(_ds(31), today=TODAY)
