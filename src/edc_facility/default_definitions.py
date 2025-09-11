from __future__ import annotations

from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE

from .constants import (
    FIVE_DAY_CLINIC,
    FOUR_DAY_CLINIC,
    SEVEN_DAY_CLINIC,
    SIX_DAY_CLINIC,
    TU_WE_TH_CLINIC,
)

default_definitions: dict[str, dict[str, list | bool]] = {
    SEVEN_DAY_CLINIC: dict(
        days=[MO, TU, WE, TH, FR, SA, SU], slots=[100, 100, 100, 100, 100, 100, 100]
    ),
    SIX_DAY_CLINIC: dict(days=[MO, TU, WE, TH, FR, SA], slots=[100, 100, 100, 100, 100, 100]),
    FIVE_DAY_CLINIC: dict(days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
    FOUR_DAY_CLINIC: dict(days=[MO, TU, WE, TH], slots=[100, 100, 100, 100]),
    TU_WE_TH_CLINIC: dict(
        days=[TU, WE, TH],
        slots=[100, 100, 100],
        best_effort_available_datetime=True,
    ),
}
