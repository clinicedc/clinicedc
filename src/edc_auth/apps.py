import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .auth_updater import AuthUpdater
from .auth_updater.group_updater import CodenameDoesNotExist
from .system_checks import edc_check

style = color_style()


def post_migrate_user_groups_and_roles(sender=None, **kwargs):  # noqa
    """Update Groups, Role model with EDC defaults."""
    from django.apps import apps as django_apps

    try:
        AuthUpdater(apps=django_apps, verbose=True)
    except CodenameDoesNotExist as e:
        sys.stdout.write(style.ERROR(f"{e}. "))
        sys.stdout.write(
            style.ERROR("\nIf the codename is mispelled, correct the error and try again.\n\n")
        )
        sys.stdout.write(
            style.ERROR("\nPut `edc_auth` as close to last as possible in INSTALLED_APPS.\n\n")
        )
        sys.stdout.write(
            style.ERROR(
                "\nIf this is happening in a migration that is creating a new model,\n"
                "the post_migrate signal that creates the new model's permissions\n"
                "might be queued to run AFTER edc_auth's post_migrate signal. Let this\n"
                "migration complete and then run `migrate` again.\n\n"
            )
        )


class AppConfig(DjangoAppConfig):
    name = "edc_auth"
    verbose_name = "Edc Authentication"

    def ready(self):
        from .site_auths import site_auths

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_auths.autodiscover()
        post_migrate.connect(post_migrate_user_groups_and_roles, sender=self)
        register(edc_check)
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
