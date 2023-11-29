from __future__ import annotations

from typing import TYPE_CHECKING

from edc_form_runners.form_runner import FormRunner

from .forms import AppointmentForm

if TYPE_CHECKING:
    from django.forms import ModelForm


class AppointmentFormRunner(FormRunner):
    def __init__(self, modelform_cls: ModelForm = None, **kwargs):
        modelform_cls = modelform_cls or AppointmentForm
        extra_fieldnames = ["appt_datetime"]
        exclude_formfields = ["appt_close_datetime"]
        super().__init__(
            modelform_cls=modelform_cls,
            extra_formfields=extra_fieldnames,
            exclude_formfields=exclude_formfields,
            **kwargs,
        )
