from __future__ import annotations

from datetime import datetime

from dateutil.relativedelta import relativedelta


def adjust_previous_end_datetime(
    previous_obj,
    refill_start_datetime: datetime,
    user_modified: str | None = None,
    modified: str | None = None,
) -> None:
    if previous_obj.refill_end_datetime != refill_start_datetime - relativedelta(minutes=1):
        previous_obj.refill_end_datetime = refill_start_datetime - relativedelta(minutes=1)
        previous_obj.number_of_days = (
            previous_obj.refill_end_datetime - previous_obj.refill_start_datetime
        ).days
        previous_obj.user_modified = user_modified or previous_obj.user_modified
        previous_obj.modified = modified or previous_obj.modified
        previous_obj.save_base(
            update_fields=[
                "refill_end_datetime",
                "number_of_days",
                "modified",
                "user_modified",
            ]
        )
