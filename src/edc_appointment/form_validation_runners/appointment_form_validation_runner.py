from __future__ import annotations

from typing import TYPE_CHECKING

from edc_data_manager.form_validation_runners import FormValidationRunner

from edc_appointment.forms import AppointmentForm

if TYPE_CHECKING:
    from django.forms import ModelForm


class AppointmentFormValidationRunner(FormValidationRunner):
    def __init__(self, modelform_cls: ModelForm = None, **kwargs):
        modelform_cls = modelform_cls or AppointmentForm
        extra_fieldnames = ["appt_datetime"]
        ignore_fieldnames = ["appt_close_datetime"]
        super().__init__(
            modelform_cls=modelform_cls,
            extra_formfields=extra_fieldnames,
            ignore_formfields=ignore_fieldnames,
            **kwargs,
        )
