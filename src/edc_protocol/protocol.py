import arrow

from dateutil.relativedelta import relativedelta
from django.conf import settings
from edc_utils import get_utcnow

from .address import Address


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

        self.protocol = getattr(settings, "EDC_PROTOCOL", "AAA000")

        # 3 digits, used for identifiers
        self.protocol_number = getattr(settings, "EDC_PROTOCOL_NUMBER", "000")

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
            "Project Title (set EDC_PROTOCOL_PROJECT_NAME)",
        )
        self.protocol_name = self.project_name
        self.disclaimer = "For research purposes only."
        self.copyright = f"2010-{get_utcnow().year}"
        self.license = "GNU GENERAL PUBLIC LICENSE Version 3"

        self.default_url_name = "home_url"
        self.physical_address = Address()
        self.postal_address = Address()

        study_open_datetime = getattr(
            settings,
            "EDC_PROTOCOL_STUDY_OPEN_DATETIME",
            arrow.utcnow().floor("hour") - relativedelta(months=1),
        )

        study_close_datetime = getattr(
            settings,
            "EDC_PROTOCOL_STUDY_CLOSE_DATETIME",
            arrow.utcnow().ceil("hour") + relativedelta(years=1),
        )
        self.rstudy_open = (
            arrow.Arrow.fromdatetime(study_open_datetime, study_open_datetime.tzinfo)
            .to("utc")
            .floor("hour")
        )
        self.rstudy_close = (
            arrow.Arrow.fromdatetime(study_close_datetime, study_close_datetime.tzinfo)
            .to("utc")
            .ceil("hour")
        )
        self.study_open_datetime = self.rstudy_open.datetime
        self.study_close_datetime = self.rstudy_close.datetime
