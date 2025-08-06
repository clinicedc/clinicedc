from argparse import ArgumentParser

from django.apps import AppConfig as DjangoAppConfig
from django.conf import ENVIRONMENT_VARIABLE, settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_sites"
    verbose_name = "Edc Sites"
    has_exportable_data = True
    default_auto_field = "django.db.models.BigAutoField"
    include_in_administration_section = True

    def ready(self) -> None:
        parser = ArgumentParser()
        _, args = parser.parse_known_args()
        django_settings_module = getattr(settings, ENVIRONMENT_VARIABLE, None)
        if (
            "migrate" in args
            and not django_settings_module
            and not [a for a in args if a.startswith("--settings")]
        ):
            raise ImproperlyConfigured(
                style.ERROR(
                    f"App `{self.verbose_name}` needs access to the correct settings module. "
                    f"Either set `{ENVIRONMENT_VARIABLE}` or pass `--settings` argument when "
                    "running `migrate` from the command line. Expected something like "
                    "`manage.py migrate --settings=my_edc.settings.live."
                )
            )
        if (
            "multisite" in settings.INSTALLED_APPS
            or "multisite.apps.Appconfig" in settings.INSTALLED_APPS
        ) and getattr(settings, "MULTISITE_REGISTER_POST_MIGRATE_SYNC_ALIAS", True):
            raise ImproperlyConfigured(
                style.ERROR(
                    "Multisite post_migrate signal `post_migrate_sync_alias` conflicts "
                    "with a post-migrate signal in 'edc-sites'. To fix the issue, "
                    "`post_migrate_sync_alias` is now registered in "
                    "`edc_appconfig.apps`. To prevent a duplicate registration, you need to "
                    "add `MULTISITE_REGISTER_POST_MIGRATE_SYNC_ALIAS = False` to your "
                    "settings.py. See also edc_appconfig.apps.py"
                )
            )
