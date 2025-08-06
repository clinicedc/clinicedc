from django.conf import settings
from django.core.checks import Error


def edc_middleware_check(
    app_configs, app_label=None, middleware_name=None, error_code=None, **kwargs
):
    errors = []
    if middleware_name not in settings.MIDDLEWARE:
        errors.append(
            Error(
                "Missing MIDDLEWARE. " f"Expected `{middleware_name}`.",
                id=f"{app_label}.{error_code or '001'}",
            )
        )
    return errors
