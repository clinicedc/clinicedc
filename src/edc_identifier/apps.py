import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style


class AppConfig(DjangoAppConfig):
    name = "edc_identifier"
    verbose_name = "Edc Identifier"
    identifier_prefix = "999"  # e.g. 066 for BHP066
    identifier_modulus = 7
    messages_written = False
    subject_identifier_pattern = "092\-[0-9\-]+"

    def ready(self):
        style = color_style()
        if not self.messages_written:
            sys.stdout.write(f"Loading {self.verbose_name} ...\n")
            if "test" not in sys.argv:
                if self.identifier_prefix == "999":
                    sys.stdout.write(
                        style.NOTICE(
                            " Warning: 'identifier_prefix' has not been explicitly set. "
                            "Using default '999'. See AppConfig.\n"
                        )
                    )
            sys.stdout.write(f" * identifier prefix: {self.identifier_prefix}\n")
            sys.stdout.write(f" * check-digit modulus: {self.identifier_modulus}\n")
            sys.stdout.write(f" Done loading {self.verbose_name}\n")
        self.messages_written = True

    def get_subject_identifier_pattern(self):
        return self.subject_identifier_pattern or f"{self.identifier_prefix}\-[0-9\-]+"


if settings.APP_NAME == "edc_identifier":

    from edc_device.apps import AppConfig as BaseEdcDeviceAppConfig
    from edc_device.constants import CLIENT

    class EdcDeviceAppConfig(BaseEdcDeviceAppConfig):
        device_role = CLIENT
        device_id = "14"
