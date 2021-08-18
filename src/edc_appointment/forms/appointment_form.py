from django import forms
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import AppointmentFormValidator
from ..models import Appointment
from ..utils import get_appt_reason_choices

appt_reason_fld = Appointment._meta.get_field("appt_reason")


class AppointmentForm(SiteModelFormMixin, FormValidatorMixin, forms.ModelForm):
    """Note, the appointment is only changed, never added,
    through this form.
    """

    form_validator_cls = AppointmentFormValidator

    class Meta:
        model = Appointment
        fields = "__all__"
        widgets = {
            "appt_reason": forms.RadioSelect(
                attrs={
                    "label": appt_reason_fld.verbose_name,
                    "required": True,
                    "help_text": appt_reason_fld.help_text,
                },
                choices=get_appt_reason_choices(),
            ),
        }
