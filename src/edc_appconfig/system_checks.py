import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.checks import Error
from django.core.management import color_style

style = color_style()


def edc_check(errors) -> list:
    sys.stdout.write(style.SQL_KEYWORD("check edc_app_name set ...\r"))
    try:
        settings.EDC_APP_NAME
    except AttributeError:
        errors.append(
            Error(
                "settings.EDC_APP_NAME not set. Use edc_auth.EdcAppConfig in the main apps.py.",
                id="settings.EDC_APP_NAME",
            )
        )
    else:
        edc_app_names = []
        for app_config in django_apps.get_app_configs():
            try:
                edc_app_name = app_config.get_edc_app_name()
            except AttributeError:
                pass
            else:
                if not edc_app_name:
                    errors.append(
                        Error(
                            (
                                "settings.EDC_APP_NAME not set. edc_auth.EdcAppConfig in your "
                                "main apps.py references this settings attr."
                            ),
                            id="settings.EDC_APP_NAME",
                        )
                    )
                else:
                    edc_app_names.append(edc_app_name)
        if not edc_app_names:
            errors.append(
                Error(
                    (
                        "Unable to determine main EDC app name. Are you using "
                        "edc_auth.EdcAppConfig in your main apps.py? Have you set "
                        "settings.EDC_APP_NAME = '<my_edc_app>'?"
                    ),
                    id="EdcAppConfig",
                )
            )
        elif len(edc_app_names) > 1:
            errors.append(
                Error(
                    (
                        "Only your one app, your main app, may use `edc_auth.EdcAppConfig. "
                        f"Got {edc_app_names}"
                    ),
                    id="EdcAppConfig",
                )
            )
    return errors
