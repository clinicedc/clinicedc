import arrow

from datetime import timedelta
from dateutil.relativedelta import relativedelta, SA, SU
from uuid import UUID

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import options
from django.db.utils import IntegrityError

from edc_registration.model_mixins import SubjectIdentifierFromRegisteredSubjectModelMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from .choices import APPT_TYPE, APPT_STATUS, COMPLETE_APPT, INCOMPLETE_APPT, CANCELLED_APPT
from .constants import IN_PROGRESS_APPT, NEW_APPT
from .exceptions import AppointmentStatusError, CreateAppointmentError
from .managers import AppointmentManager


if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class AppointmentModelMixin(TimepointModelMixin, VisitScheduleModelMixin,
                            SubjectIdentifierFromRegisteredSubjectModelMixin):

    """Mixin for the appointment model only.

    Only one appointment per subject visit+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    timepoint = models.DecimalField(
        null=True,
        decimal_places=1,
        max_digits=6,
        editable=False,
        help_text='timepoint from schedule')

    timepoint_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text='Unadjusted datetime calculated from visit schedule')

    appt_close_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text='timepoint_datetime adjusted according to the nearest available datetime for this facility')

    facility_name = models.CharField(
        max_length=25)

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

    objects = AppointmentManager()

    def __str__(self):
        return "{0}.{1}".format(self.visit_code, str(self.timepoint).split('.')[-1])

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name,
                self.visit_code, self.visit_code_sequence)

    @property
    def visit(self):
        return self.subject_visit

    @property
    def str_pk(self):
        if isinstance(self.id, UUID):
            return str(self.pk)
        return self.pk

    @property
    def title(self):
        return self.schedule.get_visit(self.visit_code).title

    @property
    def report_datetime(self):
        return self.appt_datetime

    class Meta:
        abstract = True
        unique_together = (('subject_identifier', 'visit_schedule_name', 'schedule_name',
                            'visit_code', 'visit_code_sequence'),
                           ('subject_identifier', 'visit_schedule_name', 'schedule_name',
                            'visit_code', 'timepoint'))
        ordering = ('timepoint_datetime', )


class CreateAppointmentsMixin(models.Model):

    """ Model Mixin to add fields and methods to an enrollment model to create appointments on post_save.

    Requires model mixins VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin.
    """

    facility_name = models.CharField(
        verbose_name='To which facility is this subject being enrolled?',
        max_length=25,
        default='clinic',
        help_text="The facility name is need when scheduling appointments")

    @property
    def appointment_model(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.model

    @property
    def default_appt_type(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.default_appt_type

    def create_appointments(self, base_appt_datetime=None):
        """Creates appointments when called by post_save signal.

        Timepoint datetimes are adjusted according to the available days
        in the facility."""
        app_config = django_apps.get_app_config('edc_appointment')
        appointments = []
        base_appt_datetime = base_appt_datetime or self.report_datetime
        base_appt_datetime = arrow.Arrow.fromdatetime(
            base_appt_datetime, base_appt_datetime.tzinfo).to('utc').datetime
        facility = app_config.get_facility(self.facility_name)
        timepoint_datetimes = self.timepoint_datetimes(base_appt_datetime, self.schedule)
        taken_datetimes = []
        for visit, timepoint_datetime in timepoint_datetimes:
            adjusted_timepoint_datetime = self.move_to_facility_day(facility, timepoint_datetime)
            available_datetime = facility.available_datetime(
                adjusted_timepoint_datetime, taken_datetimes=taken_datetimes)
            with transaction.atomic():
                appointment = self.update_or_create_appointment(
                    visit, available_datetime, timepoint_datetime)
                appointments.append(appointment)
            taken_datetimes.append(available_datetime)
        return appointments

    def move_to_facility_day(self, facility, dt, forward_only=None):
        """Move a date forward off of a weekend unless app_config includes weekends."""
        delta = relativedelta(days=0)
        sa_delta = relativedelta(days=2)
        su_delta = relativedelta(days=1)
        if dt.weekday() == SA.weekday and SA not in facility.days:
            delta = sa_delta
        if dt.weekday() == SU.weekday and SU not in facility.days:
            delta = su_delta
        return dt + delta

    def update_or_create_appointment(self, visit, available_datetime, timepoint_datetime):
        """Updates or creates an appointment for this subject for the visit."""
        options = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit_code=visit.code,
            visit_code_sequence=0,
            timepoint=visit.timepoint,
            facility_name=self.facility_name)
        try:
            appointment = self.appointment_model.objects.get(**options)
            if appointment.timepoint_datetime - available_datetime != timedelta(0, 0, 0):
                appointment.appt_datetime = available_datetime
                appointment.timepoint_datetime = timepoint_datetime
                appointment.save(update_fields=['appt_datetime', 'timepoint_datetime'])
        except self.appointment_model.DoesNotExist:
            try:
                appointment = self.appointment_model.objects.create(
                    **options,
                    timepoint_datetime=timepoint_datetime,
                    appt_datetime=available_datetime,
                    appt_type=self.default_appt_type)
            except IntegrityError as e:
                raise CreateAppointmentError(
                    'An \'IntegrityError\' was raised while trying to create an appointment for '
                    'model \'{}\'. Got {}. Options were {}'. format(self._meta.label_lower, str(e), options))
        return appointment

    class Meta:
        abstract = True
        visit_schedule_name = None


class CreateAppointmentsOnEligibleMixin(CreateAppointmentsMixin):
    """Same as CreateAppointmentsMixin except will check for is_eigile=True before creating."""
    def create_appointments(self, base_appt_datetime=None):
        appointments = None
        try:
            if self.is_eligible:
                appointments = super(CreateAppointmentsOnEligibleMixin, self).create_appointments(
                    base_appt_datetime)
        except AttributeError as e:
            if 'is_eligible' in str(e):
                raise CreateAppointmentError(str(e))
            raise AttributeError(str(e))
        return appointments

    class Meta:
        abstract = True
        visit_schedule_name = None


class RequiresAppointmentModelMixin(models.Model):

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not kwargs.get('update_fields'):
            self.validate_visit_code_sequence()
            if self.visit_code_sequence == 0:
                self.appt_datetime, self.timepoint_datetime = self.validate_appt_datetime()
            else:
                self.appt_datetime, self.timepoint_datetime = self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(RequiresAppointmentModelMixin, self).save(*args, **kwargs)

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
        return self.appt_datetime, base_appointment.timepoint_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        return True

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
