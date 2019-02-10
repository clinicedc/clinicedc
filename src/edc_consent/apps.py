import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings

from .constants import DEFAULT_CONSENT_GROUP


class AppConfig(DjangoAppConfig):
    name = "edc_consent"
    verbose_name = "Edc Consent"
    default_consent_group = DEFAULT_CONSENT_GROUP

    def ready(self):
        from .site_consents import site_consents
        from .signals import requires_consent_on_pre_save

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_consents.autodiscover()
        for consent in site_consents.consents:
            start = consent.start.strftime("%Y-%m-%d %Z")
            end = consent.end.strftime("%Y-%m-%d %Z")
            sys.stdout.write(f" * {consent} covering {start} to {end}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")


if settings.APP_NAME == "edc_consent":

    from datetime import datetime
    from dateutil.tz.tz import gettz
    from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
        protocol = "BHP099"
        protocol_number = "099"
        protocol_name = "TestApp"
        protocol_title = ""
        study_open_datetime = datetime(2007, 12, 31, 0, 0, 0, tzinfo=gettz("UTC"))
        study_close_datetime = datetime(2019, 12, 31, 0, 0, 0, tzinfo=gettz("UTC"))

        @property
        def site_name(self):
            return "Gaborone"
