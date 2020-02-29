import arrow

from dateutil.tz import gettz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from edc_utils import formatted_datetime

from .protocol import Protocol


def date_not_before_study_start(value):
    if value:
        protocol = Protocol()
        tzinfo = gettz(settings.TIME_ZONE)
        value_utc = arrow.Arrow.fromdate(value, tzinfo).to("utc").datetime
        if value_utc < protocol.study_open_datetime:
            opened = formatted_datetime(
                timezone.localtime(protocol.study_open_datetime)
            )
            got = formatted_datetime(timezone.localtime(value_utc))
            raise ValidationError(
                f"Invalid date. Study opened on {opened}. Got {got}. "
                f"See edc_protocol.AppConfig."
            )


def datetime_not_before_study_start(value_datetime):
    if value_datetime:
        protocol = Protocol()
        value_utc = (
            arrow.Arrow.fromdatetime(value_datetime, value_datetime.tzinfo)
            .to("utc")
            .datetime
        )
        if value_utc < protocol.study_open_datetime:
            opened = formatted_datetime(
                timezone.localtime(protocol.study_open_datetime)
            )
            got = formatted_datetime(timezone.localtime(value_utc))
            raise ValidationError(
                f"Invalid date/time. Study opened on {opened}. Got {got}."
                f"See edc_protocol.AppConfig."
            )
