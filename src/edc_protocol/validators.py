from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.utils import timezone

from edc_utils import formatted_datetime

from .research_protocol_config import ResearchProtocolConfig


def date_not_before_study_start(value):
    if value:
        protocol_config = ResearchProtocolConfig()
        value_utc = datetime(*[*value.timetuple()][0:6], tzinfo=ZoneInfo("UTC"))
        if value_utc < protocol_config.study_open_datetime:
            opened = formatted_datetime(
                timezone.localtime(protocol_config.study_open_datetime)
            )
            got = formatted_datetime(timezone.localtime(value_utc))
            raise ValidationError(
                f"Invalid date. Study opened on {opened}. Got {got}. "
                f"See edc_protocol.AppConfig."
            )


def datetime_not_before_study_start(value_datetime):
    if value_datetime:
        protocol_config = ResearchProtocolConfig()
        value_utc = value_datetime.astimezone(ZoneInfo("UTC"))
        if value_utc < protocol_config.study_open_datetime:
            opened = formatted_datetime(
                timezone.localtime(protocol_config.study_open_datetime)
            )
            got = formatted_datetime(timezone.localtime(value_utc))
            raise ValidationError(
                f"Invalid date/time. Study opened on {opened}. Got {got}."
                f"See edc_protocol.AppConfig."
            )
