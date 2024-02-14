from django.apps import apps as django_apps
from django.core.checks import CheckMessage, Warning

from .metadata_rules import site_metadata_rules


def check_for_metadata_rules(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    if not site_metadata_rules.registry:
        errors.append(
            Warning(
                "No metadata rules were loaded by site_metadata_rules.autodiscover.",
                id="edc_metadata.W001",
            )
        )
    if not django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
        errors.append(Warning("Metadata rules disabled!", id="edc_metadata.W002"))
    return errors
