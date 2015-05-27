from django.db import models
from django.core.validators import RegexValidator

from simple_history.models import HistoricalRecords

from edc_base.model.models import BaseUuidModel
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.models import VisitDefinition

from ..choices import APPT_STATUS, APPT_TYPE
from ..managers import AppointmentManager


class BaseAppointment (BaseUuidModel):
    """Base class for Appointments."""
    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)
    # this is the original calculated edc_appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated edc_appointment datetime. Do not change",
        null=True,
        editable=False)
    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default='new',
        db_index=True)
    appt_reason = models.CharField(
        verbose_name=("Reason for edc_appointment"),
        max_length=25,
        help_text=("Reason for edc_appointment"),
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
    registered_subject = models.ForeignKey(RegisteredSubject, related_name='+')

    best_appt_datetime = models.DateTimeField(null=True, editable=False)

    appt_close_datetime = models.DateTimeField(null=True, editable=False)

    study_site = models.CharField(
        max_length=25,
        null=True,
        blank=False)

    visit_definition = models.ForeignKey(
        VisitDefinition,
        related_name='+',
        verbose_name=("Visit"),
        help_text=("For tracking within the window period of a visit, use the decimal convention. "
                   "Format is NNNN.N. e.g 1000.0, 1000.1, 1000.2, etc)"))

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
        help_text=('Default for subject may be edited in admin '
                   'under section bhp_subject. See Subject Configuration.')
    )

    # history = AuditTrail()
    history = HistoricalRecords()

    objects = AppointmentManager()

    def natural_key(self):
        """Returns a natural key."""
        return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
    natural_key.dependencies = ['registration.registeredsubject', 'bhp_visit.visitdefinition']

    def get_report_datetime(self):
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New edc_appointment and
        confirms choices tuple has \'new\'; as a option."""
        if 'new' not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices '
                'tuple APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status.lower() == 'new':
            retval = True
        return retval

    class Meta:
        abstract = True
