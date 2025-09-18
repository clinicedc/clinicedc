from dataclasses import dataclass, field
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .address import Address


class EdcProtocolError(Exception):
    pass


@dataclass
class ResearchProtocolConfig:
    """Encapsulates settings attributes.

    * EDC_PROTOCOL: 6 digit alphanumeric
    * EDC_PROTOCOL_INSTITUTION_NAME
    * EDC_PROTOCOL_NUMBER: Used for identifiers NNN
    * EDC_PROTOCOL_PROJECT_NAME: Short name
        e.g. Mashi, Tshepo, Ambition, BCPP, META, INTE, etc
    * EDC_PROTOCOL_STUDY_CLOSE_DATETIME
    * EDC_PROTOCOL_STUDY_OPEN_DATETIME
    * EDC_PROTOCOL_TITLE: Long name
    * EMAIL_CONTACTS
    """

    error_msg1: str = field(
        default=(
            "Unable to set `%(attr)s`. "
            "settings.%(settings_attr)s not found. "
            "Expected something like: `%(settings_attr)s = "
            'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))`. '
            "See edc_protocol."
        ),
        init=False,
        repr=False,
    )
    error_msg2: str = field(
        default=(
            "Unable to set `%(attr)s`. "
            "Settings.%(settings_attr)s cannot be None. "
            "Expected something like: `%(settings_attr)s = "
            'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))`. '
            "See edc_protocol."
        ),
        init=False,
        repr=False,
    )

    @property
    def trial_group(self) -> str:
        return getattr(settings, "EDC_PROTOCOL_TRIAL_GROUP", "-")

    @property
    def protocol(self) -> str:
        return getattr(settings, "EDC_PROTOCOL", "AAA000")

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
    def email_contacts(self) -> str:
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
        return getattr(
            settings,
            "EDC_PROTOCOL_SUBJECT_IDENTIFIER_PATTERN",
            r"%(protocol_number)s\-[0-9\-]+" % dict(protocol_number=self.protocol_number),
        )

    @property
    def screening_identifier_pattern(self) -> str:
        return getattr(settings, "EDC_PROTOCOL_SCREENING_IDENTIFIER_PATTERN", r"[A-Z0-9]{8}")

    @property
    def study_open_datetime(self) -> datetime:
        try:
            study_open_datetime = settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME
        except AttributeError:
            raise ImproperlyConfigured(
                self.error_msg1
                % {
                    "attr": "study_open_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
                }
            )
        if not study_open_datetime:
            raise ImproperlyConfigured(
                self.error_msg2
                % {
                    "attr": "study_open_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
                }
            )
        return study_open_datetime

    @property
    def study_close_datetime(self) -> datetime:
        try:
            study_close_datetime = settings.EDC_PROTOCOL_STUDY_CLOSE_DATETIME
        except AttributeError:
            raise ImproperlyConfigured(
                self.error_msg1
                % {
                    "attr": "study_close_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
                }
            )
        if not study_close_datetime:
            raise ImproperlyConfigured(
                self.error_msg2
                % {
                    "attr": "study_close_datetime",
                    "settings_attr": "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
                }
            )
        return study_close_datetime
