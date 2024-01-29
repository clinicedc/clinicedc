from django.conf import settings
from django.core.checks import CheckMessage, Error


def check_for_edc_model(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    if not settings.USE_TZ:
        errors.append(Error("EDC requires settings.USE_TZ = True", id="settings.USE_TZ"))

    return errors
