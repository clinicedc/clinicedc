from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError

from edc_utils.text import formatted_datetime

from .research_protocol_config import ResearchProtocolConfig


def date_not_before_study_start(value):
    if value:
        protocol_config = ResearchProtocolConfig()
        dte = datetime(*[*value.timetuple()][0:6], tzinfo=ZoneInfo(settings.TIME_ZONE))
        if dte < protocol_config.study_open_datetime:
            opened = formatted_datetime(protocol_config.study_open_datetime)
            raise ValidationError(
                f"Invalid date. Study opened on {opened}. Got {formatted_datetime(dte)}. "
                f"See edc_protocol.AppConfig."
            )


def datetime_not_before_study_start(value_datetime):
    if value_datetime:
        protocol_config = ResearchProtocolConfig()
        dte = value_datetime
        if dte < protocol_config.study_open_datetime:
            opened = formatted_datetime(protocol_config.study_open_datetime)
            raise ValidationError(
                f"Invalid date/time. Study opened on {opened}. Got {formatted_datetime(dte)}."
                f"See edc_protocol.AppConfig."
            )
