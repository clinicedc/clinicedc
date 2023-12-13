import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_offstudy"
    verbose_name = "Edc Offstudy"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write("Loading {} ...\n".format(self.verbose_name))
        sys.stdout.write(" Done loading {}.\n".format(self.verbose_name))
