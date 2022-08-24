from django.core.management import color_style
from edc_utils.context_processor_check import edc_context_processor_check

style = color_style()


def context_processor_check(app_configs, **kwargs):
    return edc_context_processor_check(
        app_configs,
        app_label="edc_appointment",
        context_processor_name="edc_appointment.context_processors.constants",
        error_code=None,
        **kwargs,
    )
