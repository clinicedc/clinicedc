from __future__ import annotations

from edc_form_runners.decorators import register
from edc_form_runners.form_runner import FormRunner


@register()
class AppointmentFormRunner(FormRunner):
    model_name = "edc_appointment.appointment"
    extra_fieldnames = ["appt_datetime"]
    exclude_formfields = ["appt_close_datetime"]
