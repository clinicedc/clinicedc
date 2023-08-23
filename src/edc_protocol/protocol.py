from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from edc_utils import get_utcnow

from .address import Address


class EdcProtocolError(Exception):
    pass


class Protocol:
    """Encapsulates settings attributes:
    EDC_PROTOCOL: 6 digit alpha-numeric
    EDC_PROTOCOL_INSTITUTION_NAME
    EDC_PROTOCOL_NUMBER: Used for identifiers NNN
    EDC_PROTOCOL_PROJECT_NAME: Short name
        e.g. Mashi, Tshepo, Ambition, BCPP, META, INTE, etc
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME
    EDC_PROTOCOL_STUDY_OPEN_DATETIME
    EDC_PROTOCOL_TITLE: Long name
    EMAIL_CONTACTS
    """

    def __init__(self):
        """Set with example defaults, you will need to change from your project"""

        self.trial_group = getattr(settings, "EDC_PROTOCOL_TRIAL_GROUP", "-")
        self.protocol = getattr(settings, "EDC_PROTOCOL", "AAA000")

        # 3 digits, used for identifiers, required for live systems
        self.protocol_number = getattr(settings, "EDC_PROTOCOL_NUMBER", "000")
        if not settings.DEBUG and self.protocol_number == "000":
            raise EdcProtocolError(
                "Settings attribute `EDC_PROTOCOL_NUMBER` not defined or "
                "set to '000' while DEBUG=False."
            )

        self.protocol_title = getattr(
            settings, "EDC_PROTOCOL_TITLE", "Protocol Title (set EDC_PROTOCOL_TITLE)"
        )

        self.email_contacts = getattr(settings, "EMAIL_CONTACTS", {})

        self.institution = getattr(
            settings,
            "EDC_PROTOCOL_INSTITUTION_NAME",
            "Institution (set EDC_PROTOCOL_INSTITUTION_NAME)",
        )

        self.project_name = getattr(
            settings,
            "EDC_PROTOCOL_PROJECT_NAME",
            "Project Name (set EDC_PROTOCOL_PROJECT_NAME)",
        )
        self.protocol_name: str = self.project_name
        self.protocol_lower_name = "_".join(self.protocol_name.lower().split(" "))
        self.disclaimer = _("For research purposes only")
        self.copyright = f"2010-{get_utcnow().year}"
        self.license = "GNU GENERAL PUBLIC LICENSE Version 3"

        self.default_url_name = "home_url"
        self.physical_address = Address()
        self.postal_address = Address()

        self.subject_identifier_pattern = getattr(
            settings,
            "EDC_PROTOCOL_SUBJECT_IDENTIFIER_PATTERN",
            f"{self.protocol_number}\-[0-9\-]+",  # noqa
        )
        self.screening_identifier_pattern = getattr(
            settings, "EDC_PROTOCOL_SCREENING_IDENTIFIER_PATTERN", "[A-Z0-9]{8}"
        )
        error_msg1 = (
            "Unable to set `study_open_datetime`. "
            "Settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME not found. "
            "Expected something like: `EDC_PROTOCOL_STUDY_OPEN_DATETIME = "
            'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone)`. '
            "See edc_protocol."
        )
        error_msg2 = (
            "Unable to set `study_open_datetime`. "
            "Settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME cannot be None. "
            "Expected something like: `EDC_PROTOCOL_STUDY_OPEN_DATETIME = "
            'datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone)`. '
            "See edc_protocol."
        )
        try:
            self.study_open_datetime = settings.EDC_PROTOCOL_STUDY_OPEN_DATETIME
        except AttributeError:
            raise ImproperlyConfigured(error_msg1)
        if not self.study_open_datetime:
            raise ImproperlyConfigured(error_msg2)

        try:
            self.study_close_datetime = settings.EDC_PROTOCOL_STUDY_CLOSE_DATETIME
        except AttributeError:
            raise ImproperlyConfigured(
                error_msg1.replace(
                    "EDC_PROTOCOL_STUDY_OPEN_DATETIME", "EDC_PROTOCOL_STUDY_CLOSE_DATETIME"
                ).replace("study_open_datetime", "study_close_datetime")
            )
        if not self.study_close_datetime:
            raise ImproperlyConfigured(
                error_msg2.replace(
                    "EDC_PROTOCOL_STUDY_OPEN_DATETIME", "EDC_PROTOCOL_STUDY_CLOSE_DATETIME"
                ).replace("study_open_datetime", "study_close_datetime")
            )
