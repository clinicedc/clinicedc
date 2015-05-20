from datetime import date

from django import forms
from django.db.models import get_model
from django.core.exceptions import ValidationError

from edc.entry_meta_data.models import ScheduledEntryMetaData, RequisitionMetaData
from edc.base.form.forms import BaseModelForm

from edc_appointment import IN_PROGRESS, DONE, INCOMPLETE, NEW, CANCELLED
from edc_appointment import Appointment


class AppointmentForm(BaseModelForm):

    class Meta:
        model = Appointment

    def clean(self):

        cleaned_data = self.cleaned_data
        if self.instance:
            TimePointStatus = get_model('data_manager', 'TimePointStatus')
            TimePointStatus.check_time_point_status(appointment=self.instance, exception_cls=forms.ValidationError)
        if not cleaned_data.get("appt_datetime"):
            raise forms.ValidationError('Please provide the edc_appointment date and time.')
        appt_datetime = cleaned_data.get("appt_datetime")
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        visit_definition = cleaned_data.get("visit_definition")
        visit_instance = cleaned_data.get("visit_instance")
        self._meta.model().validate_visit_instance(exception_cls=forms.ValidationError)

        # do not create an edc_appointment unless visit_code+visit_instance=0 already exists
        # visit_instance 0 visits should be created automatically
        # create edc_appointment link is just for creating continuation edc_appointment
        if visit_instance == 0:
            raise ValidationError('Continuation edc_appointment may not have visit instance equal to 0.')
        elif not Appointment.objects.filter(
                registered_subject=registered_subject,
                visit_definition=visit_definition,
                visit_instance=0).exists():
            raise forms.ValidationError('Cannot create continuation edc_appointment for visit %s. Cannot find the original edc_appointment (visit instance equal to 0).' % (visit_definition,))
#         elif Appointment.objects.filter(
#                     registered_subject=registered_subject,
#                     visit_definition=visit_definition,
#                     visit_instance=visit_instance).exists():
#             raise TypeError('Cannot create continuation edc_appointment for visit \'{0}\' with instance \'{1}\'. Such an edc_appointment already exists.'.format(visit_definition,visit_instance))
        else:
            pass
        # check edc_appointment date relative to status
        # postive t1.days => is a future date [t1.days > 0]
        # negative t1.days => is a past date [t1.days < 0]
        # zero t1.days => now (regardless of time) [t1.days == 0]
        t1 = appt_datetime.date() - date.today()
        if appt_status == CANCELLED:
            pass
        elif appt_status == INCOMPLETE:
            pass
        elif appt_status == DONE:
            # must not be future
            if t1.days > 0:
                raise forms.ValidationError("Status is DONE so the edc_appointment date cannot be a future date. You wrote '%s'" % appt_datetime)
            # cannot be done if no visit report, but how do i get to the visit report??
            # cannot be done if bucket entries exist that are NEW
            if Appointment.objects.filter(
                registered_subject=registered_subject,
                #appt_status = IN_PROGRESS,
                visit_definition=visit_definition,
                visit_instance=visit_instance).exists():
                appointment = Appointment.objects.get(registered_subject=registered_subject,
                    #appt_status = IN_PROGRESS,
                    visit_definition=visit_definition,
                    visit_instance=visit_instance)

                if ScheduledEntryMetaData.objects.filter(appointment=appointment, entry_status='NEW').exists() or RequisitionMetaData.objects.filter(appointment=appointment, entry_status='NEW').exists():
                    self.cleaned_data['appt_status'] = INCOMPLETE
        elif appt_status == NEW:
            # must be future relative to best_appt_datetime
            #if t1.days < 0:
            #    raise forms.ValidationError("Status is NEW so the edc_appointment date must be a future date. You wrote '%s'" % appt_datetime)
            # for new appointments, no matter what, appt_datetime must be greater than
            # any existing edc_appointment for this subject and visit code
            #aggr = Appointment.objects.filter(
            #    registered_subject=registered_subject,
            #    visit_definition__code=visit_definition.code).aggregate(Max('appt_datetime'))
            #if aggr['appt_datetime__max'] != None:
            #    t1 = aggr['appt_datetime__max'] - appt_datetime
            #    if t1.days >= 0:
            #        raise forms.ValidationError("A NEW edc_appointment with edc_appointment date greater than or equal to this date already exists'. You wrote '%s'" % appt_datetime)
            pass
        elif appt_status == IN_PROGRESS:
            # check if any other appointments in progress for this registered_subject
            if Appointment.objects.filter(registered_subject=registered_subject, appt_status=IN_PROGRESS).exclude(visit_definition__code=visit_definition.code, visit_instance=visit_instance):
                appointments = Appointment.objects.filter(registered_subject=registered_subject, appt_status=IN_PROGRESS).exclude(visit_definition__code=visit_definition.code, visit_instance=visit_instance)
                raise forms.ValidationError("Another edc_appointment is 'in progress'. Update edc_appointment %s.%s before changing this scheduled edc_appointment to 'in progress'" % (appointments[0].visit_definition.code, appointments[0].visit_instance))
        else:
            raise TypeError("Unknown appt_status passed to clean method in form AppointmentForm. Got %s" % appt_status)
            #must be future

        return cleaned_data
