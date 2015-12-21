from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from simple_history.models import HistoricalRecords

from edc_appointment.constants import CLINIC_APPT
from edc_base.model.models import BaseUuidModel
from edc_calendar.calendar import Calendar
from edc_constants.constants import COMPLETE, IN_PROGRESS
from edc_constants.constants import NEW
from edc_visit_schedule.models import VisitDefinition

from ..choices import APPT_STATUS, APPT_TYPE
from ..managers import AppointmentManager


class BaseAppointment (BaseUuidModel):
    """Base class for Appointments."""

    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="")

    timepoint_datetime = models.DateTimeField(
        verbose_name="Timepoint date and time",
        null=True,
        editable=False,
        help_text="Calculated edc_appointment datetime. Do not change",
    )

    appt_status = models.CharField(
        verbose_name="Status",
        choices=APPT_STATUS,
        max_length=25,
        default=NEW
    )

    appt_type = models.CharField(
        verbose_name='Appointment type',
        choices=APPT_TYPE,
        default=CLINIC_APPT,
        max_length=20,
        help_text=(
            'Default for subject may be edited in admin '
            'under section bhp_subject. See Subject Configuration.')
    )

    visit_definition = models.ForeignKey(
        VisitDefinition,
        related_name='+',
        verbose_name="Visit",
        help_text=(
            "For tracking within the window period of a visit, use the decimal convention. "
            "Format is NNNN.N. e.g 1000.0, 1000.1, 1000.2, etc)")
    )

    visit_instance = models.IntegerField(
        verbose_name="Instance",
        validators=[RegexValidator(r'[0-9]', 'Must be a number from 0-9')],
        default=0,
        help_text=(
            "A number to represent an additional report to be included with the original "
            "visit report. (NNNN.0)")
    )

    appt_reason = models.CharField(
        verbose_name="Reason for edc_appointment",
        max_length=25,
        blank=True
    )

    contact_tel = models.CharField(
        verbose_name="Contact Telephone",
        max_length=250,
        null=True,
        blank=True
    )

    comment = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    site_code = models.CharField(
        max_length=25,
        null=True,
        blank=False)

    dashboard_type = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text='hold dashboard_type variable, set by dashboard')

    is_confirmed = models.BooleanField(default=False, editable=False)

    contact_count = models.IntegerField(default=0, editable=False)

    best_appt_datetime = models.DateTimeField(null=True, editable=False)

    appt_close_datetime = models.DateTimeField(null=True, editable=False)

    history = HistoricalRecords()

    objects = AppointmentManager()

    def natural_key(self):
        return (
            (self.visit_instance, ) +
            self.visit_definition.natural_key() + self.registered_subject.natural_key()
        )
    natural_key.dependencies = ['edc_registration.registeredsubject', 'edc_visit_schedule.visitdefinition']

    @property
    def report_datetime(self):
        return self.appt_datetime

    def validate_appt_datetime(self):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None', will raise an exception."""
        if not self.id:
            appt_datetime = self.get_best_datetime(self.appt_datetime, self.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            appt_datetime = self.change_datetime(
                self.best_appt_datetime, self.appt_datetime, self.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_visit_instance(self, using=None, exception_cls=None):
        """Confirms a 0 instance appointment exists before allowing
        a continuation appt and keep a sequence."""
        exception_cls = exception_cls or ValidationError
        if self.visit_instance > 0:
            try:
                self.__class__.objects.using(using).get(
                    registered_subject=self.registered_subject,
                    visit_definition=self.visit_definition,
                    visit_instance=0).exclude(pk=self.pk)
            except self.__class__.DoesNotExist:
                raise exception_cls(
                    'Cannot create continuation edc_appointment for visit {}. '
                    'Cannot find the original edc_appointment (visit instance equal to 0).'.format(
                        self.visit_definition,))
            if int(self.visit_instance) - 1 != 0:
                if not self.__class__.objects.using(using).filter(
                        registered_subject=self.registered_subject,
                        visit_definition=self.visit_definition,
                        visit_instance=str(int(self.visit_instance) - 1)).exists():
                    raise exception_cls(
                        'Cannot create continuation edc_appointment for visit {0}. '
                        'Expected next visit instance to be {1}. Got {2}'.format(
                            self.visit_definition,
                            str(int(self.visit_instance) - 1),
                            self.visit_instance))

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        calendar = Calendar(forward_only=False)
        if not self.id:
            self.best_appt_datetime = calendar.best_datetime(self.appt_datetime)
        self.check_window_period()
        self.validate_visit_instance(using=using)
        # AppointmentHelper().check_appt_status(self, using)
        super().save(*args, **kwargs)

    def raw_save(self, *args, **kwargs):
        """Optional save to bypass stuff going on in the default save method."""
        super().save(*args, **kwargs)

    def __str__(self):
        return "{0} {1} for {2}.{3}".format(
            self.registered_subject.subject_identifier,
            self.registered_subject.subject_type,
            self.visit_definition.code,
            self.visit_instance)

    def dashboard(self):
        """Returns a hyperink for the Admin page."""
        ret = None
        if self.appt_status == NEW:
            return NEW
        else:
            if self.registered_subject:
                if self.registered_subject.subject_identifier:
                    url = reverse(
                        'subject_dashboard_url',
                        kwargs={
                            'dashboard_type': self.registered_subject.subject_type.lower(),
                            'dashboard_model': 'edc_appointment',
                            'dashboard_id': self.pk,
                            'show': 'appointments'})
                    ret = """<a href="{url}" />dashboard</a>""".format(url=url)
        return ret
    dashboard.allow_tags = True

    @property
    def subject_identifier(self):
        """Returns the subject identifier."""
        return self.registered_subject.subject_identifier

    @property
    def is_complete(self):
        return self.appt_status == COMPLETE

    @property
    def is_new(self):
        return self.appt_status == NEW

    @property
    def is_in_progress(self):
        return self.appt_status == IN_PROGRESS

    class Meta:
        abstract = True
