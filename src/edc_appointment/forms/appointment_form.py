from datetime import date

from django import forms

from edc_meta_data.models import CrfMetaData, RequisitionMetaData
from edc_constants.constants import IN_PROGRESS, COMPLETE_APPT, INCOMPLETE, CANCELLED, NEW_APPT, UNKEYED

from ..models import Appointment


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = '__all__'

    def clean(self):
        cleaned_data = super(AppointmentForm, self).clean()
        self.validate_time_point_status()
        self.validate_visit_instance()
        self.validate_appt_date_if_status_complete()
        return cleaned_data

    def clean_appt_datetime(self):
        appt_datetime = self.cleaned_data['appt_datetime']
        if not appt_datetime:
            raise forms.ValidationError('Please provide the appointment date and time.')
        return appt_datetime

    def validate_time_point_status(self):
        if self.instance:
            self.instance.time_point_status_open_or_raise(exception_cls=forms.ValidationError)

    def validate_visit_instance(self):
        instance = Appointment(**self.cleaned_data)
        Appointment.validate_visit_instance(instance, exception_cls=forms.ValidationError)

    def validate_appt_date_if_status_complete(self):
        cleaned_data = self.cleaned_data
        appt_datetime = cleaned_data.get("appt_datetime")
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        visit_definition = cleaned_data.get("visit_definition")
        visit_instance = cleaned_data.get("visit_instance")
        t1 = appt_datetime.date() - date.today()
        if appt_status == CANCELLED:
            pass
        elif appt_status == INCOMPLETE:
            pass
        elif appt_status == COMPLETE_APPT:
            # must not be future
            if t1.days > 0:
                raise forms.ValidationError(
                    'Status is COMPLETE_APPT so the appointment date cannot be a future date. '
                    'You wrote \'{}\''.format(appt_datetime))
            # cannot be done if no visit report, but how do i get to the visit report??
            # cannot be done if bucket entries exist that are UNKEYED
            if Appointment.objects.filter(
                    registered_subject=registered_subject,
                    visit_definition=visit_definition,
                    visit_instance=visit_instance).exists():
                appointment = Appointment.objects.get(
                    registered_subject=registered_subject,
                    visit_definition=visit_definition,
                    visit_instance=visit_instance)
                if (CrfMetaData.objects.filter(appointment=appointment, entry_status=UNKEYED).exists() or
                        RequisitionMetaData.objects.filter(appointment=appointment, entry_status=UNKEYED).exists()):
                    self.cleaned_data['appt_status'] = INCOMPLETE
        elif appt_status == NEW_APPT:
            pass
        elif appt_status == IN_PROGRESS:
            # check if any other appointments in progress for this registered_subject
            if Appointment.objects.filter(
                    registered_subject=registered_subject, appt_status=IN_PROGRESS).exclude(
                        visit_definition__code=visit_definition.code, visit_instance=visit_instance):
                appointments = Appointment.objects.filter(
                    registered_subject=registered_subject, appt_status=IN_PROGRESS).exclude(
                        visit_definition__code=visit_definition.code, visit_instance=visit_instance)
                raise forms.ValidationError(
                    "Another appointment is 'in progress'. Update appointment {}.{} before changing "
                    "this scheduled appointment to 'in progress'".format(
                        appointments[0].visit_definition.code, appointments[0].visit_instance))
        else:
            raise TypeError(
                "Unknown appt_status passed to clean method in form AppointmentForm. Got {}".format(appt_status))
