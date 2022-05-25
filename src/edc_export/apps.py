import os

from django.apps import AppConfig as DjangoApponfig
from django.conf import settings


class AppConfig(DjangoApponfig):
    name = "edc_export"
    verbose_name = "Edc Export"
    export_folder = os.path.join(settings.MEDIA_ROOT, "edc_export", "export")
    upload_folder = os.path.join(settings.MEDIA_ROOT, "edc_export", "upload")
    include_in_administration_section = True
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):

        os.makedirs(self.export_folder, exist_ok=True)
        os.makedirs(self.upload_folder, exist_ok=True)


if settings.APP_NAME == "edc_export":

    from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
        }
