from django.core.management import color_style
from edc_utils.context_processors_check import edc_context_processors_check

style = color_style()


def context_processors_check(app_configs, **kwargs):
    return edc_context_processors_check(
        app_configs,
        app_label="edc_appointment",
        context_processor_name="edc_appointment.context_processors.constants",
        error_code=None,
        **kwargs,
    )
