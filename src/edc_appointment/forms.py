from django import forms
from edc_appointment.modelform_mixins import AppointmentFormMixin
from edc_appointment.models import Appointment


class AppointmentForm(AppointmentFormMixin, forms.ModelForm):

    # NOTE: if you need to change choices, do something like this.
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         if self.instance and self.instance.status_field is not None:
    #             self.fields['appt_reason'].choices = APPOINTMENT_REASON
    #             self.fields['appt_reason'].widget.choices = APPOINTMENT_REASON

    class Meta:
        model = Appointment
        fields = '__all__'
