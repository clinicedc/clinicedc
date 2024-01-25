import sys

from django.conf import settings
from django.core.checks import Error
from django.core.management import color_style

style = color_style()


def check_for_edc_appconfig(errors) -> list:
    """Check for edc_appconfig in INSTALLED_APPS.

    Register in edc_auth
    """
    sys.stdout.write(style.SQL_KEYWORD("check for edc_appconfig ...\r"))
    if "edc_appconfig.apps.AppConfig" not in settings.INSTALLED_APPS:
        errors.append(
            Error(
                "edc_appconfig is not in INSTALLED_APPS.",
                id="edc_appconfig.001",
            )
        )
    if "edc_appconfig.apps.AppConfig" != settings.INSTALLED_APPS[-1:][0]:
        errors.append(
            Error(
                "edc_appconfig should be the last app in INSTALLED_APPS. "
                f"Got {settings.INSTALLED_APPS[-1:]}",
                id="edc_appconfig.002",
            )
        )
    sys.stdout.write(style.SQL_KEYWORD("check for edc_appconfig ... done\n"))

    return errors
