import sys

from django.conf import settings
from django.core.checks import Error
from django.core.management import color_style

style = color_style()


def edc_middleware_check(
    app_configs, app_label=None, middleware_name=None, error_code=None, **kwargs
):
    msg = f"check for {app_label}.middleware"
    sys.stdout.write(style.SQL_KEYWORD(f"{msg} ... \r"))
    errors = []
    if middleware_name not in settings.MIDDLEWARE:
        errors.append(
            Error(
                "Missing MIDDLEWARE. " f"Expected `{middleware_name}`.",
                id=f"{app_label}.{error_code or'001'}",
            )
        )
    sys.stdout.write(style.SQL_KEYWORD(f"{msg} ... done.\n"))
    return errors
