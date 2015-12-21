from datetime import date

from django import forms
from django.db.models import get_model
from django.core.exceptions import ValidationError

from edc.entry_meta_data.models import ScheduledEntryMetaData, RequisitionMetaData

from edc_constants.constants import IN_PROGRESS, COMPLETE_APPT, INCOMPLETE, CANCELLED, NEW_APPT, UNKEYED


from ..models import Appointment


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

    def clean(self):

        cleaned_data = self.cleaned_data
        if self.instance:
            TimePointStatus = get_model('data_manager', 'TimePointStatus')
            TimePointStatus.check_time_point_status(appointment=self.instance, exception_cls=forms.ValidationError)
        if not cleaned_data.get("appt_datetime"):
            raise forms.ValidationError('Please provide the appointment date and time.')
        appt_datetime = cleaned_data.get("appt_datetime")
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        visit_definition = cleaned_data.get("visit_definition")
        visit_instance = cleaned_data.get("visit_instance")
        self._meta.model().validate_visit_instance(exception_cls=forms.ValidationError)
        if visit_instance == 0:
            raise ValidationError(
                'Continuation appointment may not have visit instance equal to 0.')
        elif not Appointment.objects.filter(
                registered_subject=registered_subject,
                visit_definition=visit_definition,
                visit_instance=0).exists():
            raise forms.ValidationError(
                'Cannot create continuation appointment for visit {}. Cannot find the original '
                'appointment (visit instance equal to 0).'.format(visit_definition,))
        else:
            pass
        # check appointment date relative to status
        # postive t1.days => is a future date [t1.days > 0]
        # negative t1.days => is a past date [t1.days < 0]
        # zero t1.days => now (regardless of time) [t1.days == 0]
        t1 = appt_datetime.date() - date.today()
        if appt_status == CANCELLED:
            pass
        elif appt_status == INCOMPLETE:
            pass
        elif appt_status == COMPLETE_APPT:
            # must not be future
            if t1.days > 0:
                raise forms.ValidationError(
                    "Status is COMPLETE_APPT so the appointment date cannot be a future date. You wrote '%s'" % appt_datetime)
            # cannot be done if no visit report, but how do i get to the visit report??
            # cannot be done if bucket entries exist that are UNKEYED
            if Appointment.objects.filter(registered_subject=registered_subject,
                                          visit_definition=visit_definition,
                                          visit_instance=visit_instance).exists():
                appointment = Appointment.objects.get(
                    registered_subject=registered_subject,
                    visit_definition=visit_definition,
                    visit_instance=visit_instance)
                if (ScheduledEntryMetaData.objects.filter(appointment=appointment, entry_status=UNKEYED).exists() or
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
        return cleaned_data
