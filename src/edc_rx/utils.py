from __future__ import annotations

from typing import Any


class TotalDaysMismatch(Exception):
    pass


def validate_total_days(form: Any, rx_days: int | None = None) -> None:
    rx_days = rx_days or form.cleaned_data.get("rx_days") or 0
    clinic_days = form.cleaned_data.get("clinic_days") or 0
    club_days = form.cleaned_data.get("club_days") or 0
    purchased_days = form.cleaned_data.get("purchased_days") or 0

    total_days = clinic_days + club_days + purchased_days
    if total_days != rx_days:
        raise TotalDaysMismatch(
            f"Patient to return for a drug refill in {rx_days} days. "
            f"Check that the total days supplied "
            f"({clinic_days} + {club_days} + {purchased_days}) matches this."
        )
