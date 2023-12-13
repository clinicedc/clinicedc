import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site import get_autodiscover_sites, sites

style = color_style()


def post_migrate_update_sites(sender=None, **kwargs):
    from edc_sites.utils import add_or_update_django_sites

    sys.stdout.write(style.MIGRATE_HEADING("Updating sites:\n"))

    for country in sites.countries:
        sys.stdout.write(style.MIGRATE_HEADING(f" (*) sites for {country} ...\n"))
        add_or_update_django_sites(verbose=True)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoAppConfig):
    name = "edc_sites"
    verbose_name = "Edc Sites"
    has_exportable_data = True
    default_auto_field = "django.db.models.BigAutoField"
    include_in_administration_section = True

    def ready(self):
        if get_autodiscover_sites():
            post_migrate.connect(post_migrate_update_sites, sender=self)
            sys.stdout.write(f"Loading {self.verbose_name} ...\n")
            sites.autodiscover()
