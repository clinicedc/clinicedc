from datetime import datetime, time
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from multisite.utils import get_multisite_timezone


class TrialDates:
    error_msg1: str = (
        "Unable to set `%(attr)s`. "
        "settings.%(settings_attr)s not found. "
        "Expected something like: `%(settings_attr)s = "
        'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))`. '
        "See edc_protocol."
    )
    error_msg2: str = (
        "Unable to set `%(attr)s`. "
        "Settings.%(settings_attr)s cannot be None. "
        "Expected something like: `%(settings_attr)s = "
        'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))`. '
        "See edc_protocol."
    )

    def __init__(self, site_id: int | None = None):
        self.site_id = site_id

    @property
    def study_open_datetime(self) -> datetime:
        """Returns a datetime in the local timezone with the time
        normalized down without adjusting for any offset.
        """
        try:
            study_open_datetime = settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME
        except AttributeError as e:
            raise ImproperlyConfigured(
                self.error_msg1
                % {
                    "attr": "study_open_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
                }
            ) from e
        if not study_open_datetime:
            raise ImproperlyConfigured(
                self.error_msg2
                % {
                    "attr": "study_open_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
                }
            )

        # keep the exact calendar year, month, and day -- do not calculate the offset
        return datetime.combine(
            study_open_datetime.date(),
            time.min,
            tzinfo=ZoneInfo(get_multisite_timezone(self.site_id)),
        )

    @property
    def study_close_datetime(self) -> datetime:
        """Returns a datetime in the local timezone with the time
        normalized up without adjusting for any offset.
        """
        try:
            study_close_datetime = settings.EDC_PROTOCOL_STUDY_CLOSE_DATETIME
        except AttributeError as e:
            raise ImproperlyConfigured(
                self.error_msg1
                % {
                    "attr": "study_close_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
                }
            ) from e
        if not study_close_datetime:
            raise ImproperlyConfigured(
                self.error_msg2
                % {
                    "attr": "study_close_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
                }
            )
        # keep the exact calendar year, month, and day -- do not calculate the offset
        return datetime.combine(
            study_close_datetime.date(),
            time.max,
            tzinfo=ZoneInfo(get_multisite_timezone(self.site_id)),
        )

    @property
    def study_close_grace_period_datetime(self) -> datetime:
        """Returns a datetime on or after the study close datetime
        based on the number of months and calendar unit read from
        settings.EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD.

        For example in settings.py:
            EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD = (3, "months")

        The default is no grace period.

        See also: delete_appointments_after_study_close_grace_period()
        """

        if grace_period := getattr(settings, "EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD", ()):
            months, attrname = grace_period
            return self.study_close_datetime + relativedelta(**{attrname: months})
        return self.study_close_datetime


# with a mulitsite multi-timezone project
# instantiate late with the site_id
trial_dates = TrialDates()
