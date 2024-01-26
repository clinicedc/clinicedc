from django.core.checks import CheckMessage, Error

from edc_consent import site_consents


def check_site_consents(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    if not site_consents.registry:
        errors.append(
            Error("No consent definitions have been registered.", id="edc_consent.E001")
        )
    return errors
