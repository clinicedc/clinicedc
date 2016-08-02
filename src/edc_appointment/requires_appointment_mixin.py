from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction

from edc_constants.constants import (
    COMPLETE_APPT, NEW_APPT, CANCELLED, INCOMPLETE, UNKEYED, IN_PROGRESS)

from .appointment_date_helper import AppointmentDateHelper
from .choices import APPT_STATUS
from .exceptions import AppointmentStatusError
from .window_period_helper import WindowPeriodHelper


class RequiresAppointmentMixin(models.Model):

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not kwargs.get('update_fields'):
            self.validate_visit_code_sequence()
            if self.visit_code_sequence == 0:
                self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
            else:
                self.appt_datetime, self.best_appt_datetime = self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(RequiresAppointmentMixin, self).save(*args, **kwargs)

    @property
    def date_helper(self):
        return AppointmentDateHelper(self.__class__)

    def get_appt_status(self, using):
        """Returns the appt_status by checking the meta data entry status for all required CRFs and requisitions.
        """
        from edc_meta_data.helpers import CrfMetaDataHelper
        appt_status = self.appt_status
        visit_model = self.visit_definition.visit_tracking_content_type_map.model_class()
        try:
            visit_code_sequence = visit_model.objects.get(appointment=self)
            crf_meta_data_helper = CrfMetaDataHelper(self, visit_code_sequence)
            if not crf_meta_data_helper.show_entries():
                appt_status = COMPLETE_APPT
            else:
                if appt_status in [COMPLETE_APPT, INCOMPLETE]:
                    appt_status = INCOMPLETE if self.unkeyed_forms() else COMPLETE_APPT
                elif appt_status in [NEW_APPT, CANCELLED, IN_PROGRESS]:
                    appt_status = IN_PROGRESS
                    self.update_others_as_not_in_progress(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(self.appt_status))
        except visit_model.DoesNotExist:
            if self.appt_status not in [NEW_APPT, CANCELLED]:
                appt_status = NEW_APPT
        return appt_status

    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    def validate_visit_code_sequence(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        visit_code_sequence = self.visit_code_sequence or 0
        if self.visit_code_sequence != 0:
            previous = str(int(visit_code_sequence) - 1)
            try:
                appointment = self.appointment_model.objects.get(
                    appointment_identifier=self.appointment_identifier,
                    visit_code=self.visit_code,
                    visit_code_sequence=previous)
                if appointment.id == self.id:
                    raise self.appointment_model.DoesNotExist
            except self.appointment_model.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_code, visit_code_sequence))

    def update_others_as_not_in_progress(self, using):
        """Updates other appointments for this registered subject to not be IN_PROGRESS.

        Only one appointment can be "in_progress", so look for any others in progress and change
        to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""

        for appointment in self.appointment_model.objects.filter(
                appointment_identifier=self.appointment_identifier,
                appt_status=IN_PROGRESS).exclude(
                    pk=self.pk):
            with transaction.atomic(using):
                if self.unkeyed_forms():
                    if appointment.appt_status != INCOMPLETE:
                        appointment.appt_status = INCOMPLETE
                        appointment.save(using, update_fields=['appt_status'])
                else:
                    if appointment.appt_status != COMPLETE_APPT:
                        appointment.appt_status = COMPLETE_APPT
                        appointment.save(using, update_fields=['appt_status'])

    def unkeyed_forms(self):
        if self.unkeyed_crfs() or self.unkeyed_requisitions():
            return True
        return False

    def unkeyed_crfs(self):
        from edc_meta_data.helpers import CrfMetaDataHelper
        return CrfMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def unkeyed_requisitions(self):
        from edc_meta_data.helpers import RequisitionMetaDataHelper
        return RequisitionMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        base_appointment = self.appointment_model.objects.get(
            appointment_identifier=self.appointment_identifier,
            visit_code=self.visit_code,
            visit_code_sequence=0)
        if self.visit_code_sequence != 0 and (self.appt_datetime - base_appointment.appt_datetime).days < 1:
            raise exception_cls(
                'Appointment date must be a future date relative to the '
                'base appointment. Got {} not greater than {} at {}.0.'.format(
                    self.appt_datetime.strftime('%Y-%m-%d'),
                    base_appointment.appt_datetime.strftime('%Y-%m-%d'),
                    self.visit_code))
        return self.appt_datetime, base_appointment.best_appt_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id and self.visit_code_sequence == 0:
            window_period = WindowPeriodHelper(
                self.visit_code, self.appt_datetime, self.best_appt_datetime)
            if not window_period.check_datetime():
                raise exception_cls(window_period.error_message)

    def time_point(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return """<a href="{url}?appointment_identifier={appointment_identifier}" />time_point</a>""".format(
            url=url, appointment_identifier=self.appointment_identifier)
    time_point.allow_tags = True

    def get_report_datetime(self):
        """Returns the appointment datetime as the report_datetime."""
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New appointment and confirms choices
        tuple has \'new\'; as a option."""
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
        """Returns True if the appointment status is COMPLETE_APPT."""
        return self.appt_status == COMPLETE_APPT

    class Meta:
        abstract = True
