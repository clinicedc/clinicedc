from django import forms
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import AppointmentFormValidator
from ..models import Appointment


class AppointmentForm(SiteModelFormMixin, FormValidatorMixin, forms.ModelForm):
    """Note, the appointment is only changed, never added,
    through this form.
    """

    form_validator_cls = AppointmentFormValidator

    class Meta:
        model = Appointment
        fields = "__all__"
