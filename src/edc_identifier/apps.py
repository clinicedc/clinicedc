import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_identifier"
    verbose_name = "Edc Identifier"
    identifier_modulus = 7
    messages_written = False
    include_in_administration_section = True

    def ready(self):
        if not self.messages_written:
            sys.stdout.write(f"Loading {self.verbose_name} ...\n")
            sys.stdout.write(f" * check-digit modulus: {self.identifier_modulus}\n")
            sys.stdout.write(f" Done loading {self.verbose_name}\n")
        self.messages_written = True
