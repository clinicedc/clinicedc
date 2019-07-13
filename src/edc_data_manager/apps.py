import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_data_manager import site_data_manager


style = color_style()


def populate_data_dictionary(sender=None, **kwargs):
    from .populate_data_dictionary import populate_data_dictionary_from_sites

    sys.stdout.write(style.MIGRATE_HEADING("Populating data dictionary:\n"))
    populate_data_dictionary_from_sites()
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


def update_query_rule_handlers(sender=None, **kwargs):
    sys.stdout.write(
        style.MIGRATE_HEADING(
            "Deactivating query rules with invalid rule handler names:\n"
        )
    )
    handler_names = [x for x in site_data_manager.registry.keys()]
    django_apps.get_model("edc_data_manager.queryrule").objects.exclude(
        rule_handler_name__in=handler_names
    ).update(active=False)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoAppConfig):
    name = "edc_data_manager"
    verbose_name = "Data Management"
    description = ""
    admin_site_name = "edc_data_manager_admin"
    include_in_administration_section = True
    has_exportable_data = True

    def ready(self):
        post_migrate.connect(populate_data_dictionary, sender=self)
        post_migrate.connect(update_query_rule_handlers, sender=self)

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_data_manager.autodiscover()


if settings.APP_NAME == "edc_data_manager":

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            "data_manager_app": ("subject_visit", "data_manager_app.subjectvisit")
        }

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(
                days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
            ),
        }

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        pass

    class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
        reason_field = {"data_manager_app.subjectvisit": "reason"}
