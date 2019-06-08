import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate


style = color_style()


def populate_data_dictionary(sender=None, **kwargs):
    from .populate_data_dictionary import populate_data_dictionary_from_sites
    sys.stdout.write(style.MIGRATE_HEADING(
        "Populating data dictionary:\n"))
    populate_data_dictionary_from_sites()
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoAppConfig):
    name = "edc_data_manager"
    verbose_name = "Data Management"
    admin_site_name = "edc_data_manager_admin"

    def ready(self):
        post_migrate.connect(populate_data_dictionary, sender=self)
