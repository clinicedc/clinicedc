import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class EdcOffstudyAppConfigError(Exception):
    pass


ATTR = 0
MODEL_LABEL = 1


class AppConfig(DjangoAppConfig):
    name = "edc_offstudy"
    verbose_name = "Edc Offstudy"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        # from .signals import offstudy_model_on_post_save

        sys.stdout.write("Loading {} ...\n".format(self.verbose_name))
        sys.stdout.write(" Done loading {}.\n".format(self.verbose_name))


if settings.APP_NAME == "edc_offstudy":
    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(
                days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
            ),
            "3-day-clinic": dict(
                days=[TU, WE, TH],
                slots=[100, 100, 100],
                best_effort_available_datetime=True,
            ),
        }
