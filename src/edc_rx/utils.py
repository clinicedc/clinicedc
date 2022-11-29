from __future__ import annotations

from typing import Any


class TotalDaysMismatch(Exception):
    pass


def validate_total_days(form: Any, return_in_days: int | None = None) -> None:
    return_in_days = return_in_days or form.cleaned_data.get("return_in_days")
    if (
        form.cleaned_data.get("clinic_days")
        and form.cleaned_data.get("club_days")
        and form.cleaned_data.get("purchased_days")
        and int(return_in_days or 0)
    ):
        total = (
            form.cleaned_data.get("clinic_days")
            or 0 + form.cleaned_data.get("club_days")
            or 0 + form.cleaned_data.get("purchased_days")
            or 0
        )
        if total != int(return_in_days or 0):
            raise TotalDaysMismatch(
                f"Patient to return for a drug refill in {return_in_days} days. "
                "Check that the total days match."
            )
