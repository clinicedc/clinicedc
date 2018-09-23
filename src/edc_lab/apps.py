import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_labs import site_labs

style = color_style()


def update_panels_on_post_migrate(sender, **kwargs):
    site_labs.migrated = True
    site_labs.autodiscover()
    if site_labs.loaded:
        site_labs.update_panel_model(
            panel_model_cls=sender.get_model('panel'),
            sender=sender)


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    has_exportable_data = True

    def ready(self):
        from .models.signals import manifest_item_on_post_delete
        post_migrate.connect(update_panels_on_post_migrate, sender=self)
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_labs.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
