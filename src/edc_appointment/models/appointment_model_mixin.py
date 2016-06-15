from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, transaction
from simple_history.models import HistoricalRecords as AuditTrail

from edc_base.model.models import BaseUuidModel
from edc_constants.constants import COMPLETE_APPT, NEW_APPT, CLOSED, CANCELLED, INCOMPLETE, UNKEYED, IN_PROGRESS
from edc_sync.models import SyncModelMixin
from edc_visit_schedule.models import VisitDefinition

from ..choices import APPT_TYPE, APPT_STATUS
from ..exceptions import AppointmentStatusError
from ..managers import AppointmentManager

from .appointment_date_helper import AppointmentDateHelper
from .time_point_status import TimePointStatus
from .window_period_helper import WindowPeriodHelper


class AppointmentModelMixin(models.Model):
    """Tracks appointments for a registered subject's visit.

        Only one appointment per subject visit_definition+visit_instance.
        Attribute 'visit_instance' should be populated by the system.
    """

    visit_definition = models.ForeignKey(
        VisitDefinition,
        related_name='+',
        verbose_name="Visit",
        help_text=("For tracking within the window period of a visit, use the decimal convention. "
                   "Format is NNNN.N. e.g 1000.0, 1000.1, 1000.2, etc)"))

    best_appt_datetime = models.DateTimeField(null=True, editable=False)

    appt_close_datetime = models.DateTimeField(null=True, editable=False)

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
    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)

    # this is the original calculated appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated appointment datetime. Do not change",
        null=True,
        editable=False)

    time_point_status = models.ForeignKey(TimePointStatus, null=True, blank=True)

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

    contact_tel = models.CharField(
        verbose_name=("Contact Tel"),
        max_length=250,
        blank=True)

    comment = models.CharField(
        "Comment",
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    contact_count = models.IntegerField(default=0, editable=False)

    dashboard_type = models.CharField(
        max_length=25,
        editable=False,
        null=True,
        blank=True,
        db_index=True,
        help_text='hold dashboard_type variable, set by dashboard')

    appt_type = models.CharField(
        verbose_name='Appointment type',
        choices=APPT_TYPE,
        default='clinic',
        max_length=20,
        help_text=(
            'Default for subject may be edited in admin under section bhp_subject. '
            'See Subject Configuration.'))

    objects = AppointmentManager()

    history = AuditTrail()

    def __unicode__(self):
        return "{0} {1} for {2}.{3}".format(
            self.registered_subject.subject_identifier, self.registered_subject.subject_type,
            self.visit_definition.code, self.visit_instance)

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
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
        super(Appointment, self).save(*args, **kwargs)

    def natural_key(self):
        """Returns a natural key."""
        return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
    natural_key.dependencies = ['edc_registration.registeredsubject', 'edc_visit_schedule.visitdefinition']

    def validate_visit_instance(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        self.visit_instance = self.visit_instance or '0'
        if self.visit_instance != '0':
            previous = str(int(self.visit_instance) - 1)
            try:
                appointment = Appointment.objects.get(
                    registered_subject=self.registered_subject,
                    visit_definition=self.visit_definition,
                    visit_instance=previous)
                if appointment.id == self.id:
                    raise Appointment.DoesNotExist
            except Appointment.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_definition.code, self.visit_instance))

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

    def update_others_as_not_in_progress(self, using):
        """Updates other appointments for this registered subject to not be IN_PROGRESS.

        Only one appointment can be "in_progress", so look for any others in progress and change
        to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""

        for appointment in self.__class__.objects.filter(
                registered_subject=self.registered_subject, appt_status=IN_PROGRESS).exclude(
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
                subject_identifier=self.registered_subject.subject_identifier)

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper(self.__class__)
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(
                self.appt_datetime, self.registered_subject.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime,
                self.registered_subject.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        base_appointment = self.__class__.objects.get(
            registered_subject=self.registered_subject,
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

    def dashboard(self):
        """Returns a hyperink for the Admin page."""
        ret = None
        if settings.APP_NAME == 'cancer':
            if self.registered_subject:
                if self.registered_subject.subject_identifier:
                    url = reverse('subject_dashboard_url',
                                  kwargs={'dashboard_type': self.registered_subject.subject_type.lower(),
                                          'dashboard_model': 'appointment',
                                          'dashboard_id': self.pk,
                                          'show': 'appointments'})
                    ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        if self.appt_status == APPT_STATUS[0][0]:
            if settings.APP_NAME != 'cancer':
                return NEW_APPT
        else:
            if self.registered_subject:
                if self.registered_subject.subject_identifier:
                    url = reverse('subject_dashboard_url',
                                  kwargs={'dashboard_type': self.registered_subject.subject_type.lower(),
                                          'dashboard_model': 'appointment',
                                          'dashboard_id': self.pk,
                                          'show': 'appointments'})
                    ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True

    def time_point(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return """<a href="{url}?subject_identifier={subject_identifier}" />time_point</a>""".format(
            url=url, subject_identifier=self.registered_subject.subject_identifier)
    time_point.allow_tags = True

    def get_subject_identifier(self):
        """Returns the subject identifier."""
        return self.registered_subject.subject_identifier

    def get_registered_subject(self):
        """Returns the registered subject."""
        return self.registered_subject

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

    def dispatch_container_lookup(self):
        return (self.__class__, 'id')

    def is_dispatched(self):
        """Returns the dispatched status based on the visit tracking
        form's id_dispatched response."""
        Visit = self.visit_definition.visit_tracking_content_type_map.model_class()
        return Visit.objects.get(appointment=self).is_dispatched()

    def include_for_dispatch(self):
        return True

    class Meta:
        app_label = 'edc_appointment'
        unique_together = (('registered_subject', 'visit_definition', 'visit_instance'),)
        ordering = ['registered_subject', 'appt_datetime', ]
