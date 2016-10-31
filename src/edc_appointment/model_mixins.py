from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import options

from edc_registration.model_mixins import RegisteredSubjectMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .appointment_date_helper import AppointmentDateHelper
from .choices import APPT_TYPE, APPT_STATUS, COMPLETE_APPT, INCOMPLETE_APPT, CANCELLED_APPT
from .constants import IN_PROGRESS_APPT, NEW_APPT
from .exceptions import AppointmentStatusError
from .window_period_helper import WindowPeriodHelper
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class CreateAppointmentsMixin(models.Model):

    """ Model Mixin to add methods to an enrollment model to create appointments on post_save.

    Model must have field `report_datetime`"""

    def create_appointments(self, base_appt_datetime=None):
        """Creates appointments when called by post_save signal. """
        appointments = []
        app_config = django_apps.get_app_config('edc_appointment')
        visit_schedule = site_visit_schedules.get_visit_schedule(self._meta.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self._meta.label_lower)
        base_appt_datetime = base_appt_datetime or self.report_datetime
        for visit in schedule.visits:
            with transaction.atomic():
                appointment = self.update_or_create_appointment(
                    visit_schedule=visit_schedule,
                    schedule=schedule,
                    visit=visit,
                    subject_identifier=self.subject_identifier,
                    appt_datetime=base_appt_datetime,
                    default_appt_type=app_config.default_appt_type)
                appointments.append(appointment)
        return appointments

    def update_or_create_appointment(self, visit_schedule=None, schedule=None, visit=None, subject_identifier=None,
                                     appt_datetime=None, default_appt_type=None):
        """Updates or creates an appointment for this subject for the visit."""
        # TODO: commented out for now, there is transaction condition if used
        # appt_datetime = self.new_appointment_appt_datetime(appt_datetime, visit)
        appointment_model = django_apps.get_app_config('edc_appointment').model
        created = False
        try:
            appointment = appointment_model.objects.get(
                subject_identifier=subject_identifier,
                visit_code=visit.code,
                visit_code_sequence=0)
            td = appointment.best_appt_datetime - appt_datetime
            if td.days == 0 and abs(td.seconds) > 59:
                # the calculated appointment date does not match
                # the best_appt_datetime (not within 59 seconds)
                # which means you changed the date on the membership form and now
                # need to correct the best_appt_datetime
                appointment.appt_datetime = appt_datetime
                appointment.best_appt_datetime = appt_datetime
                appointment.save(update_fields=['appt_datetime', 'best_appt_datetime'])
        except appointment_model.DoesNotExist:
            appointment = appointment_model.objects.create(
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule.name,
                schedule_name=schedule.name,
                visit_code=visit.code,
                visit_code_sequence=0,
                best_appt_datetime=appt_datetime,
                appt_datetime=appt_datetime,
                appt_type=default_appt_type)
            created = True
        return appointment, created

    @property
    def appointment_date_helper(self):
        appointment_model = django_apps.get_app_config('edc_appointment').model
        return AppointmentDateHelper(appointment_model)

    def new_appointment_appt_datetime(self, report_datetime, visit):
        """Calculates and returns the appointment date for new appointments."""
        if visit.timepoint == 0:
            appt_datetime = self.appointment_date_helper.get_best_datetime(
                report_datetime)
        else:
            appt_datetime = self.get_relative_datetime(
                report_datetime, visit.code)
        return appt_datetime

    def get_relative_datetime(self, base_appt_datetime, visit):
        """ Returns appointment datetime relative to the base_appointment_datetime."""
        visit_schedule = site_visit_schedules.get_visit_schedule(self.create_appointments_visit_schedule)
        schedule = visit_schedule.get_schedule(self._meta.label_lower)
        appt_datetime = base_appt_datetime + schedule.relativedelta_from_base(visit)
        return self.appointment_date_helper.get_best_datetime(appt_datetime, base_appt_datetime.isoweekday())

    class Meta:
        visit_schedule_name = None
        abstract = True


class AppointmentModelMixin(TimepointModelMixin, VisitScheduleModelMixin, RegisteredSubjectMixin):

    """Mixin for the appointment model.

    Only one appointment per subject visit+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    best_appt_datetime = models.DateTimeField(null=True, editable=False)

    appt_close_datetime = models.DateTimeField(null=True, editable=False)

    # TODO: can this be removed? use visit_code_sequence?
    visit_instance = models.CharField(
        max_length=1,
        verbose_name=("Instance"),
        validators=[RegexValidator(r'[0-9]', 'Must be a number from 0-9')],
        default='0',
        null=True,
        blank=True,
        db_index=True,
        help_text=("A decimal to represent an additional report to be included with the original "
                   "visit report. (NNNN.0)"))

    visit_code_sequence = models.IntegerField(
        verbose_name=("Sequence"),
        default=0,
        null=True,
        blank=True,
        help_text=("An integer to represent the sequence of additional appointments "
                   "relative to the base appointment, 0, needed to complete data "
                   "collection for the timepoint. (NNNN.0)"))

    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)

    appt_type = models.CharField(
        verbose_name='Appointment type',
        choices=APPT_TYPE,
        default='clinic',
        max_length=20,
        help_text=(
            'Default for subject may be edited Subject Configuration.'))

    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True)

    appt_reason = models.CharField(
        verbose_name=("Reason for appointment"),
        max_length=25,
        help_text=("Reason for appointment"),
        blank=True)

    comment = models.CharField(
        "Comment",
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return "{0}.{1}".format(
            self.visit_code, self.visit_code_sequence)

    @property
    def title(self):
        return self.schedule.get_visit(self.visit_code).title

    @property
    def report_datetime(self):
        return self.appt_datetime

    class Meta:
        abstract = True
        unique_together = (('subject_identifier', 'visit_schedule_name', 'schedule_name',
                            'visit_code', 'visit_code_sequence'), )


class RequiresAppointmentModelMixin(models.Model):

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
        super(RequiresAppointmentModelMixin, self).save(*args, **kwargs)

    @property
    def date_helper(self):
        return AppointmentDateHelper(self.__class__)

    def get_appt_status(self, using='default'):
        """Returns the appt_status by checking the meta data entry status for all required CRFs and requisitions.
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
                    appt_status = INCOMPLETE_APPT if self.unkeyed_forms() else COMPLETE_APPT
                elif appt_status in [NEW_APPT, CANCELLED_APPT, IN_PROGRESS_APPT]:
                    appt_status = IN_PROGRESS_APPT
                    self.update_others_as_not_in_progress(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(self.appt_status))
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
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_code, visit_code_sequence))

#     def update_others_as_not_in_progress(self, using):
#         """Updates other appointments for this registered subject to not be IN_PROGRESS_APPT.
#
#         Only one appointment can be "in_progress", so look for any others in progress and change
#         to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""
#
#         appointment_model = django_apps.get_app_config('edc_appointment').model
#         for appointment in appointment_model.objects.filter(
#                 appointment_identifier=self.appointment_identifier,
#                 appt_status=IN_PROGRESS_APPT).exclude(
#                     pk=self.pk):
#             with transaction.atomic(using):
#                 if self.unkeyed_forms():
#                     if appointment.appt_status != INCOMPLETE_APPT:
#                         appointment.appt_status = INCOMPLETE_APPT
#                         appointment.save(using, update_fields=['appt_status'])
#                 else:
#                     if appointment.appt_status != COMPLETE_APPT:
#                         appointment.appt_status = COMPLETE_APPT
#                         appointment.save(using, update_fields=['appt_status'])
#
#     def unkeyed_forms(self):
#         if self.unkeyed_crfs() or self.unkeyed_requisitions():
#             return True
#         return False
#
#     def unkeyed_crfs(self):
#         from edc_metadata.helpers import CrfMetaDataHelper
#         return CrfMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)
#
#     def unkeyed_requisitions(self):
#         from edc_metadata.helpers import RequisitionMetaDataHelper
#         return RequisitionMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.
        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        # for tests
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper()
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(self.appt_datetime)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime, self.visit_definition, self.visit_code)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        appointment_model = django_apps.get_app_config('edc_appointment').model
        base_appointment = appointment_model.objects.get(
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
                self.visit_definition,
                self.visit_code, self.appt_datetime, self.best_appt_datetime)
            if not window_period.check_datetime():
                raise exception_cls(window_period.error_message)

    def timepoint(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return """<a href="{url}?appointment_identifier={appointment_identifier}" />timepoint</a>""".format(
            url=url, appointment_identifier=self.appointment_identifier)
    timepoint.allow_tags = True

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
