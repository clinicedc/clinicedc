from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from edc.core.bhp_variables.models import StudySite
from edc.core.bhp_variables.utils import default_study_site
from edc.subject.registration.models import RegisteredSubject
from edc_visit_schedule.classes import WindowPeriod
from edc_visit_schedule.models import VisitDefinition
from edc_base.audit_trail import AuditTrail
from edc_constants.constants import COMPLETE_APPT, NEW_APPT

from ..choices import APPT_TYPE, APPT_STATUS
from ..managers import AppointmentManager

from .appointment_helper import AppointmentHelper
from .appointment_date_helper import AppointmentDateHelper
from .base_appointment import BaseAppointment


class Appointment(BaseAppointment):
    """Tracks appointments for a registered subject's visit.

        Only one appointment per subject visit_definition+visit_instance.
        Attribute 'visit_instance' should be populated by the system.
    """
    registered_subject = models.ForeignKey(
        RegisteredSubject,
        related_name='+')

    study_site = models.ForeignKey(
        StudySite,
        null=True,
        blank=False,
        default=lambda: default_study_site('site_code', settings.SITE_CODE))

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
        if self.id:
            TimePointStatus = models.get_model('data_manager', 'TimePointStatus')
            TimePointStatus.check_time_point_status(self, using=using)
        self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
        self.check_window_period()
        self.validate_visit_instance(using=using)
        AppointmentHelper().check_appt_status(self, using)
        super(Appointment, self).save(*args, **kwargs)

    def raw_save(self, *args, **kwargs):
        """Optional save to bypass stuff going on in the default save method."""
        super(Appointment, self).save(*args, **kwargs)

    def natural_key(self):
        """Returns a natural key."""
        return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
    natural_key.dependencies = ['registration.registeredsubject', 'bhp_visit.visitdefinition']

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        # for tests
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper(self.__class__)
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(self.appt_datetime, self.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime, self.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_visit_instance(self, using=None, exception_cls=None):
        """Confirms a 0 instance appointment exists before allowing a continuation
        appt and keep a sequence."""
        if not exception_cls:
            exception_cls = ValidationError
        if not isinstance(self.visit_instance, basestring):
            raise exception_cls('Expected \'visit_instance\' to be of type basestring')
        if self.visit_instance != '0':
            if not Appointment.objects.using(using).filter(
                    registered_subject=self.registered_subject,
                    visit_definition=self.visit_definition,
                    visit_instance='0').exclude(pk=self.pk).exists():
                raise exception_cls(
                    'Cannot create continuation appointment for visit {}. Cannot find the original '
                    'appointment (visit instance equal to 0).'.format(self.visit_definition,))
            if int(self.visit_instance) - 1 != 0:
                if not Appointment.objects.using(using).filter(
                        registered_subject=self.registered_subject,
                        visit_definition=self.visit_definition,
                        visit_instance=str(int(self.visit_instance) - 1)).exists():
                    raise exception_cls(
                        'Cannot create continuation appointment for visit {0}. '
                        'Expected next visit instance to be {1}. Got {2}'.format(
                            self.visit_definition, str(int(self.visit_instance) - 1), self.visit_instance))

    def check_window_period(self, exception_cls=None):
        """Is this used?"""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id:
            window_period = WindowPeriod()
            if not window_period.check_datetime(self.visit_definition, self.appt_datetime, self.best_appt_datetime):
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

    def get_subject_identifier(self):
        """Returns the subject identifier."""
        return self.registered_subject.subject_identifier

    def get_registered_subject(self):
        """Returns the registered subject."""
        return self.registered_subject

    def get_report_datetime(self):
        """Returns the appointment datetime as the report_datetime."""
        return self.appt_datetime

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
        db_table = 'bhp_appointment_appointment'
        unique_together = (('registered_subject', 'visit_definition', 'visit_instance'),)
        ordering = ['registered_subject', 'appt_datetime', ]
