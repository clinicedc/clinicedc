from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


from django.apps import apps as django_apps

fqdn = "edc_data_manager.clinicedc.org"

my_sites = ((10, "gaborone", "Gaborone"),)


def post_migrate_update_sites(sender=None, **kwargs):
    from edc_sites.utils import add_or_update_django_sites

    add_or_update_django_sites(
        apps=django_apps, sites=my_sites, fqdn=fqdn, verbose=True
    )


class AppConfig(DjangoAppConfig):
    name = "edc_data_manager"

    def ready(self):
        if settings.APP_NAME == "edc_data_manager":
            post_migrate.connect(post_migrate_update_sites, sender=self)
