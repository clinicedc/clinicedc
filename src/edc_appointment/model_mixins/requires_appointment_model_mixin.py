from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from ..choices import APPT_STATUS, COMPLETE_APPT, INCOMPLETE_APPT, CANCELLED_APPT
from ..constants import IN_PROGRESS_APPT, NEW_APPT
from ..exceptions import AppointmentStatusError


class RequiresAppointmentModelMixin(models.Model):

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not kwargs.get('update_fields'):
            self.validate_visit_code_sequence()
            if self.visit_code_sequence == 0:
                self.appt_datetime, self.timepoint_datetime = \
                    self.validate_appt_datetime()
            else:
                self.appt_datetime, self.timepoint_datetime = \
                    self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(RequiresAppointmentModelMixin, self).save(*args, **kwargs)

    def get_appt_status(self, using='default'):
        """Returns the appt_status by checking the meta data entry
        status for all required CRFs and requisitions.
        """
        from edc_metadata.helpers import CrfMetaDataHelper
        appt_status = self.appt_status
        visit_model = self.visit_definition.visit_model
        try:
            visit_code_sequence = visit_model.objects.get(appointment=self)
            crf_meta_data_helper = CrfMetaDataHelper(self, visit_code_sequence)
            if not crf_meta_data_helper.show_entries():
                appt_status = COMPLETE_APPT
            else:
                if appt_status in [COMPLETE_APPT, INCOMPLETE_APPT]:
                    appt_status = INCOMPLETE_APPT if self.unkeyed_forms(
                    ) else COMPLETE_APPT
                elif appt_status in [NEW_APPT, CANCELLED_APPT, IN_PROGRESS_APPT]:
                    appt_status = IN_PROGRESS_APPT
                    self.update_others_as_not_in_progress(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(
                            self.appt_status))
        except visit_model.DoesNotExist:
            if self.appt_status not in [NEW_APPT, CANCELLED_APPT]:
                appt_status = NEW_APPT
        return appt_status

    def validate_visit_code_sequence(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        visit_code_sequence = self.visit_code_sequence or 0
        appointment_model = django_apps.get_app_config('edc_appointment').model
        if self.visit_code_sequence != 0:
            previous = str(int(visit_code_sequence) - 1)
            try:
                appointment = appointment_model.objects.get(
                    appointment_identifier=self.appointment_identifier,
                    visit_code=self.visit_code,
                    visit_code_sequence=previous)
                if appointment.id == self.id:
                    raise appointment_model.DoesNotExist
            except appointment_model.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of '
                    'sequence. Got \'{}.{}\'.'.format(
                        self.visit_code, visit_code_sequence))

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        appointment_model = django_apps.get_app_config('edc_appointment').model
        base_appointment = appointment_model.objects.get(
            appointment_identifier=self.appointment_identifier,
            visit_code=self.visit_code,
            visit_code_sequence=0)
        if (self.visit_code_sequence != 0
                and (self.appt_datetime
                     - base_appointment.appt_datetime).days < 1):
            raise exception_cls(
                'Appointment date must be a future date relative to the '
                'base appointment. Got {} not greater than {} at {}.0.'.format(
                    self.appt_datetime.strftime('%Y-%m-%d'),
                    base_appointment.appt_datetime.strftime('%Y-%m-%d'),
                    self.visit_code))
        return self.appt_datetime, base_appointment.timepoint_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        return True

    def timepoint(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return (
            """<a href='{url}?appointment_identifier={appointment_identifier}''
            ' />timepoint</a>""".format(
                url=url, appointment_identifier=self.appointment_identifier))
    timepoint.allow_tags = True

    def get_report_datetime(self):
        """Returns the appointment datetime as the report_datetime.
        """
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New appointment and confirms choices
        tuple has \'new\'; as a option.
        """
        if NEW_APPT not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices tuple '
                'APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status == NEW_APPT:
            retval = True
        return retval

    @property
    def complete(self):
        """Returns True if the appointment status is COMPLETE_APPT.
        """
        return self.appt_status == COMPLETE_APPT

    class Meta:
        abstract = True
