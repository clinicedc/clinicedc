from datetime import date, datetime

from django.core.exceptions import ValidationError

from edc_utils.text import formatted_date, formatted_datetime

from .trial_dates import trial_dates


def date_not_before_study_start(value: date | None) -> None:
    if value and value < trial_dates.study_open_datetime.date():
        opened = formatted_date(trial_dates.study_open_datetime)
        raise ValidationError(
            f"Invalid date. Study opened on {opened}. Got {formatted_date(value)}. "
        )


def datetime_not_before_study_start(value_datetime: datetime | None) -> None:
    if value_datetime and value_datetime < trial_dates.study_open_datetime:
        opened = formatted_datetime(trial_dates.study_open_datetime)
        raise ValidationError(
            f"Invalid date/time. Study opened on {opened}. "
            f"Got {formatted_datetime(value_datetime)}."
        )
