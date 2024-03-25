from django.conf import settings
from django.core.checks import Error


def edc_context_processors_check(
    app_configs, app_label=None, context_processor_name=None, error_code=None, **kwargs
):
    errors = []
    for template_config in settings.TEMPLATES:
        if context_processor_name not in template_config.get("OPTIONS").get(
            "context_processors"
        ):
            errors.append(
                Error(
                    "Missing item in TEMPLATE.OPTIONS.context_processors. "
                    f"Expected `{context_processor_name}`.",
                    id=f"{app_label}.{error_code or '001'}",
                )
            )
    return errors
