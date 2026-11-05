"""Sensor gates of the canvod-airflow DAGs.

Deciding when a sensor pokes again, gives up or lets the run continue is
orchestration, not processing, so it lives here and not in
``canvodpy.workflows.tasks``.
"""

from __future__ import annotations

import datetime as dt

from airflow.sdk import PokeReturnValue  # type: ignore[unresolved-import]
from airflow.sdk.exceptions import (
    AirflowSkipException,  # type: ignore[unresolved-import]
)

#: Days after which the SP3/CLK products of a day are expected, per
#: ``processing.aux_data.product_type``.
SP3_MIN_AGE_DAYS: dict[str, int] = {"rapid": 2, "final": 14}

#: Days after which the sensor gives up on a day's SP3/CLK products.
SP3_ABANDON_AGE_DAYS = 30


def check_sp3_availability(ds: str, today: dt.date | None = None) -> PokeReturnValue:
    """Return a ``PokeReturnValue`` for the SP3/CLK date-age sensor.

    The products of a day count as available once the day is old enough
    for ``processing.aux_data.product_type``:

    * ``rapid``: 2 days
    * ``final``: 14 days

    Falls back to ``final`` when the settings can't be loaded.

    Parameters
    ----------
    ds : str
        Airflow ``ds`` value (``YYYY-MM-DD``).
    today : datetime.date, optional
        The date to measure the age against; today's date when omitted.

    Raises
    ------
    AirflowSkipException
        When the day is more than 30 days old, so runs for old days don't
        wait forever.
    """
    target = dt.date.fromisoformat(ds)
    age = ((today or dt.date.today()) - target).days

    if age > SP3_ABANDON_AGE_DAYS:
        raise AirflowSkipException(f"SP3 not available for {ds} after {age} days; abandoning")

    try:
        from canvod.config import load_config

        product_type = load_config().processing.aux_data.product_type
    except Exception:
        product_type = "final"

    min_age = SP3_MIN_AGE_DAYS[product_type]
    available = age >= min_age

    return PokeReturnValue(
        is_done=available,
        xcom_value={
            "sp3_ready": available,
            "product_type": product_type,
            "age_days": age,
            "min_age_days": min_age,
        },
    )
