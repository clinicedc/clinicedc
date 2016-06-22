from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction
from simple_history.models import HistoricalRecords as AuditTrail

from edc_constants.constants import COMPLETE_APPT, NEW_APPT, CLOSED, CANCELLED, INCOMPLETE, UNKEYED, IN_PROGRESS

from ..choices import APPT_STATUS
from ..exceptions import AppointmentStatusError

from .appointment_date_helper import AppointmentDateHelper
from .time_point_status import TimePointStatus
from .window_period_helper import WindowPeriodHelper


class RequiresAppointmentMixin(models.Model):

    APPOINTMENT_MODEL = None

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not self.subject_registration_instance():
            raise ValidationError("Subject registration instance can not be null.")
        if not kwargs.get('update_fields'):
            self.validate_visit_instance()
            if self.id:
                self.time_point_status_open_or_raise()
            if self.visit_instance == '0':
                self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
            else:
                self.appt_datetime, self.best_appt_datetime = self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(RequiresAppointmentMixin, self).save(*args, **kwargs)

#     def natural_key(self):
#         """Returns a natural key."""
#         return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
#     natural_key.dependencies = ['edc_registration.registeredsubject', 'edc_visit_schedule.visitdefinition']

    def get_appt_status(self, using):
        """Returns the appt_status by checking the meta data entry status for all required CRFs and requisitions.
        """
        from edc_meta_data.models import CrfMetaDataHelper
        appt_status = self.appt_status
        visit_model = self.visit_definition.visit_tracking_content_type_map.model_class()
        try:
            visit_instance = visit_model.objects.get(appointment=self)
            crf_meta_data_helper = CrfMetaDataHelper(self, visit_instance)
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

    def validate_visit_instance(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        visit_instance = self.visit_instance or '0'
        if self.visit_instance != '0':
            previous = str(int(visit_instance) - 1)
            try:
                appointment = self.APPOINTMENT_MODEL.objects.get(
                    appointment_identifier=self.appointment_identifier,
                    visit_definition=self.visit_definition,
                    visit_instance=previous)
                if appointment.id == self.id:
                    raise self.APPOINTMENT_MODEL.DoesNotExist
            except self.APPOINTMENT_MODEL.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_definition.code, visit_instance))

    def update_others_as_not_in_progress(self, using):
        """Updates other appointments for this registered subject to not be IN_PROGRESS.

        Only one appointment can be "in_progress", so look for any others in progress and change
        to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""

        for appointment in self.APPOINTMENT_MODEL.objects.filter(
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

    def subject_registration_instance(self):
        """Returns the subject registration instance.

        Overide this method at the APPOINTMENT_MODEL"""
        return None

    def unkeyed_crfs(self):
        from edc_meta_data.models import CrfMetaDataHelper
        return CrfMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def unkeyed_requisitions(self):
        from edc_meta_data.models import RequisitionMetaDataHelper
        return RequisitionMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def time_point_status_open_or_raise(self, exception_cls=None):
        """Checks the timepoint status and prevents edits to the model if
        time_point_status_status == closed."""
        exception_cls = exception_cls or ValidationError
        try:
            if self.time_point_status.status == CLOSED:
                raise ValidationError('Data entry for this time point is closed. See TimePointStatus.')
        except AttributeError:
            pass
        except TimePointStatus.DoesNotExist:
            self.time_point_status = TimePointStatus.objects.create(
                visit_code=self.visit_definition.code,
                appointment_identifier=self.appointment_identifier)  # TODO quesry with someything that uniquely idetifier all other subject's appointments

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper(self.APPOINTMENT_MODEL)
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(
                self.appt_datetime, self.subject_registration_instance.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime,
                self.subject_registration_instance.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        base_appointment = self.APPOINTMENT_MODEL.objects.get(
            appointment_identifier=self.appointment_identifier,
            visit_definition=self.visit_definition,
            visit_instance='0')
        if self.visit_instance != '0' and (self.appt_datetime - base_appointment.appt_datetime).days < 1:
            raise exception_cls(
                'Appointment date must be a future date relative to the '
                'base appointment. Got {} not greater than {} at {}.0.'.format(
                    self.appt_datetime.strftime('%Y-%m-%d'),
                    base_appointment.appt_datetime.strftime('%Y-%m-%d'),
                    self.visit_definition.code))
        return self.appt_datetime, base_appointment.best_appt_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id and self.visit_instance == '0':
            window_period = WindowPeriodHelper(
                self.visit_definition, self.appt_datetime, self.best_appt_datetime)
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