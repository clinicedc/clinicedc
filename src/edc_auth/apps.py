import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .update_roles import update_roles
from .system_checks import edc_check


style = color_style()


def post_migrate_user_roles(sender=None, **kwargs):
    update_roles(verbose=True)


class AppConfig(DjangoAppConfig):
    name = "edc_auth"
    verbose_name = "Edc Authentication"

    def ready(self):
        post_migrate.connect(post_migrate_user_roles, sender=self)
        register(edc_check)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
