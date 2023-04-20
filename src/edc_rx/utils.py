from __future__ import annotations

from typing import Any


class TotalDaysMismatch(Exception):
    pass


def validate_total_days(form: Any, return_in_days: int | None = None) -> None:
    return_in_days = return_in_days or form.cleaned_data.get("return_in_days") or 0
    clinic_days = form.cleaned_data.get("clinic_days") or 0
    club_days = form.cleaned_data.get("club_days") or 0
    purchased_days = form.cleaned_data.get("purchased_days") or 0

    total_days = clinic_days + club_days + purchased_days
    if total_days != return_in_days:
        raise TotalDaysMismatch(
            f"Patient to return for a drug refill in {return_in_days} days. "
            f"Check that the total days supplied "
            f"({clinic_days} + {club_days} + {purchased_days}) matches this."
        )
