from __future__ import annotations

from django import forms
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyNonCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import VisitScheduleNonCrfModelFormMixin

from ..form_validators import AppointmentFormValidator
from ..models import Appointment
from ..utils import get_appointment_form_meta_options

appt_reason_fld = Appointment._meta.get_field("appt_reason")
appt_type_fld = Appointment._meta.get_field("appt_type")


class AppointmentForm(
    SiteModelFormMixin,
    VisitScheduleNonCrfModelFormMixin,
    OffstudyNonCrfModelFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
    forms.ModelForm,
):
    """Note, the appointment is only changed, never added,
    through this form.
    """

    form_validator_cls = AppointmentFormValidator
    report_datetime_field_attr: str = "appt_datetime"

    class Meta:
        model = Appointment
        fields = "__all__"
        labels = get_appointment_form_meta_options()["labels"]
        help_texts = get_appointment_form_meta_options()["help_texts"]
