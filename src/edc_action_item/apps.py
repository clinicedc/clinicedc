import sys

from django.apps import AppConfig as DjangoApponfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_action_items import site_action_items

style = color_style()


def update_action_types(sender=None, verbose=None, **kwargs):  # noqa

    sys.stdout.write(style.MIGRATE_HEADING("Updating action types:\n"))
    site_action_items.create_or_update_action_types()
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoApponfig):
    name = "edc_action_item"
    verbose_name = "Action Items"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        post_migrate.connect(update_action_types, sender=self)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_action_items.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
