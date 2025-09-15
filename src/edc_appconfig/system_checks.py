from django.conf import settings
from django.core.checks import CheckMessage, Error
from django.core.management import color_style

style = color_style()

__all__ = ["check_for_edc_appconfig"]


def check_for_edc_appconfig(app_configs, **kwargs) -> list[CheckMessage]:
    """Check for edc_appconfig in INSTALLED_APPS.

    Register in edc_auth
    """
    errors = []
    if getattr(settings, "EDC_APPCONFIG_SYSTEM_CHECK_ENABLED", True):
        if "edc_appconfig.apps.AppConfig" not in settings.INSTALLED_APPS:
            errors.append(
                Error(
                    "edc_appconfig is not in INSTALLED_APPS.",
                    id="edc_appconfig.E001",
                )
            )
        if settings.INSTALLED_APPS[-1:][0] != "edc_appconfig.apps.AppConfig":
            errors.append(
                Error(
                    "edc_appconfig should be the last app in INSTALLED_APPS. "
                    f"Got {settings.INSTALLED_APPS[-1:]}",
                    id="edc_appconfig.E002",
                )
            )
    return errors
