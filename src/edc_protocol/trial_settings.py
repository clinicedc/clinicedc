from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .address import Address


class EdcProtocolError(Exception):
    pass


class TrialSettings:
    """Encapsulates settings attributes.

    * EDC_PROTOCOL: 6 digit alphanumeric
    * EDC_PROTOCOL_INSTITUTION_NAME
    * EDC_PROTOCOL_NUMBER: Used for identifiers NNN
    * EDC_PROTOCOL_PROJECT_NAME: Short name
        e.g. Mashi, Tshepo, Ambition, BCPP, META, INTE, etc
    * EDC_PROTOCOL_STUDY_CLOSE_DATETIME
    * EDC_PROTOCOL_STUDY_OPEN_DATETIME
    * EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD (months after close to accept data)
    * EDC_PROTOCOL_TITLE: Long name
    * EMAIL_CONTACTS
    """

    trial_group: str = getattr(settings, "EDC_PROTOCOL_TRIAL_GROUP", "-")
    protocol: str = getattr(settings, "EDC_PROTOCOL", "AAA000")

    @property
    def protocol_number(self) -> str:
        """3 digits, used for identifiers, required for live systems"""
        protocol_number = getattr(settings, "EDC_PROTOCOL_NUMBER", "000")
        if not settings.DEBUG and protocol_number == "000":
            raise EdcProtocolError(
                "Settings attribute `EDC_PROTOCOL_NUMBER` not defined or "
                "set to '000' while DEBUG=False."
            )

        return protocol_number

    @property
    def protocol_title(self) -> str:
        return getattr(
            settings, "EDC_PROTOCOL_TITLE", "Protocol Title (set EDC_PROTOCOL_TITLE)"
        )

    @property
    def email_contacts(self) -> dict[str, str]:
        return getattr(settings, "EMAIL_CONTACTS", {})

    @property
    def institution(self) -> str:
        return getattr(
            settings,
            "EDC_PROTOCOL_INSTITUTION_NAME",
            "Institution (set EDC_PROTOCOL_INSTITUTION_NAME)",
        )

    @property
    def project_name(self) -> str:
        return getattr(
            settings,
            "EDC_PROTOCOL_PROJECT_NAME",
            "Project Name (set EDC_PROTOCOL_PROJECT_NAME)",
        )

    @property
    def protocol_name(self) -> str:
        return self.project_name

    @property
    def protocol_lower_name(self) -> str:
        return "_".join(self.protocol_name.lower().split(" "))

    @property
    def protocol_module_prefix(self) -> str:
        return getattr(
            settings,
            "EDC_PROTOCOL_MODULE_PREFIX",
            "",
        )

    @property
    def disclaimer(self) -> str:
        return _("For research purposes only")

    @property
    def copyright(self) -> str:
        return f"2010-{timezone.now().year}"

    @property
    def license(self) -> str:
        return "GNU GENERAL PUBLIC LICENSE Version 3"

    @property
    def default_url_name(self) -> str:
        return "home_url"

    @property
    def physical_address(self) -> Address:
        return Address()

    @property
    def postal_address(self) -> Address:
        return Address()

    @property
    def subject_identifier_pattern(self) -> str:
        default_pattern = r"\b" + self.protocol_number + r"-\d{2}-\d{4}-\d{1}\b"
        return getattr(
            settings,
            "EDC_PROTOCOL_SUBJECT_IDENTIFIER_PATTERN",
            default_pattern,
        )

    @property
    def screening_identifier_pattern(self) -> str:
        return getattr(settings, "EDC_PROTOCOL_SCREENING_IDENTIFIER_PATTERN", r"[A-Z0-9]{8}")

    # @property
    # def study_open_datetime(self) -> datetime:
    #     """Returns a datetime in the local timezone with the time
    #     normalized down without adjusting for any offset.
    #     """
    #     try:
    #         study_open_datetime = settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME
    #     except AttributeError as e:
    #         raise ImproperlyConfigured(
    #             self.error_msg1
    #             % {
    #                 "attr": "study_open_datetime",
    #                 "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
    #             }
    #         ) from e
    #     if not study_open_datetime:
    #         raise ImproperlyConfigured(
    #             self.error_msg2
    #             % {
    #                 "attr": "study_open_datetime",
    #                 "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
    #             }
    #         )
    #
    #     # keep the exact calendar year, month, and day -- do not calculate the offset
    #     return datetime.combine(
    #         study_open_datetime.date(), time.min, tzinfo=ZoneInfo(get_multisite_timezone())
    #     )
    #
    # @property
    # def study_close_datetime(self) -> datetime:
    #     """Returns a datetime in the local timezone with the time
    #     normalized up without adjusting for any offset.
    #     """
    #     try:
    #         study_close_datetime = settings.EDC_PROTOCOL_STUDY_CLOSE_DATETIME
    #     except AttributeError as e:
    #         raise ImproperlyConfigured(
    #             self.error_msg1
    #             % {
    #                 "attr": "study_close_datetime",
    #                 "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
    #             }
    #         ) from e
    #     if not study_close_datetime:
    #         raise ImproperlyConfigured(
    #             self.error_msg2
    #             % {
    #                 "attr": "study_close_datetime",
    #                 "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
    #             }
    #         )
    #     # keep the exact calendar year, month, and day -- do not calculate the offset
    #     return datetime.combine(
    #         study_close_datetime.date(), time.max, tzinfo=ZoneInfo(get_multisite_timezone())
    #     )
    #
    # @property
    # def study_close_grace_period_datetime(self) -> datetime:
    #     """Returns a datetime on or after the study close datetime
    #     based on the number of months and calendar unit read from
    #     settings.EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD.
    #
    #     For example in settings.py:
    #         EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD = (3, "months")
    #
    #     The default is no grace period.
    #
    #     See also: delete_appointments_after_study_close_grace_period()
    #     """
    #
    #     if grace_period := getattr(settings, "EDC_PROTOCOL_STUDY_CLOSE_GRACE_PERIOD", ()):
    #         months, attrname = grace_period
    #         return self.study_close_datetime + relativedelta(**{attrname: months})
    #     return self.study_close_datetime


trial_settings = TrialSettings()
