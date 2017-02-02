from uuid import UUID

from django.core.validators import RegexValidator
from django.db import models

from edc_registration.model_mixins import (
    SubjectIdentifierFromRegisteredSubjectModelMixin)
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from ..choices import APPT_TYPE, APPT_STATUS
from ..constants import NEW_APPT
from ..managers import AppointmentManager


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
        help_text=(
            'timepoint_datetime adjusted according to the nearest '
            'available datetime for this facility'))

    facility_name = models.CharField(
        max_length=25)

    # TODO: can this be removed? use visit_code_sequence?
    visit_instance = models.CharField(
        max_length=1,
        verbose_name=('Instance'),
        validators=[RegexValidator(r'[0-9]', 'Must be a number from 0-9')],
        default='0',
        null=True,
        blank=True,
        db_index=True,
        help_text=('A decimal to represent an additional report to be '
                   'included with the original visit report. (NNNN.0)'))

    visit_code_sequence = models.IntegerField(
        verbose_name=('Sequence'),
        default=0,
        null=True,
        blank=True,
        help_text=('An integer to represent the sequence of additional '
                   'appointments relative to the base appointment, 0, needed '
                   'to complete data collection for the timepoint. (NNNN.0)'))

    appt_datetime = models.DateTimeField(
        verbose_name=('Appointment date and time'),
        help_text='',
        db_index=True)

    appt_type = models.CharField(
        verbose_name='Appointment type',
        choices=APPT_TYPE,
        default='clinic',
        max_length=20,
        help_text=(
            'Default for subject may be edited Subject Configuration.'))

    appt_status = models.CharField(
        verbose_name=('Status'),
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True)

    appt_reason = models.CharField(
        verbose_name=('Reason for appointment'),
        max_length=25,
        help_text=('Reason for appointment'),
        blank=True)

    comment = models.CharField(
        'Comment',
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    objects = AppointmentManager()

    def __str__(self):
        return '{0}.{1}'.format(
            self.visit_code, str(self.timepoint).split('.')[-1])

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name,
                self.visit_code,
                self.visit_code_sequence)

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
        unique_together = (
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'visit_code', 'visit_code_sequence'),
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'visit_code', 'timepoint')
        )
        ordering = ('timepoint_datetime', )
