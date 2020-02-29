import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = "edc_appointment"
    verbose_name = "Edc Appointments"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        from .signals import (
            create_appointments_on_post_save,  # noqa
            appointment_post_save,  # noqa
            appointments_on_pre_delete,  # noqa
        )

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
