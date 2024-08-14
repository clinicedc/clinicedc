from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import Tags, register
from django.core.management.color import color_style
from edc_appconfig.system_checks import check_for_edc_appconfig

from .system_checks import (
    check_auth_updater,
    check_etc_dir,
    check_key_path,
    check_site_auths,
    check_static_root,
)

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_auth"
    verbose_name = "Edc Authentication"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        register(check_etc_dir, Tags.security, deploy=True)
        register(check_key_path, Tags.security, deploy=True)
        register(check_static_root, Tags.security, deploy=True)
        register(check_site_auths)
        register(check_auth_updater)
        register(check_for_edc_appconfig)
