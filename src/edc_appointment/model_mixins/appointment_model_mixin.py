from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin
from uuid import UUID

from ..choices import APPT_TYPE, APPT_STATUS, APPT_REASON
from ..constants import NEW_APPT
from ..managers import AppointmentManager


class AppointmentModelMixin(NonUniqueSubjectIdentifierFieldMixin,
                            TimepointModelMixin, VisitScheduleModelMixin):

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
        db_index=True,
        help_text=(
            'If the visit has already begun, only \'in progress\' or '
            '\'incomplete\' are valid options'))

    appt_reason = models.CharField(
        verbose_name=('Reason for appointment'),
        max_length=25,
        choices=APPT_REASON,
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
        if self.visit_code_sequence > 0:
            title = (f'{self.schedule.visits.get(self.visit_code).title} '
                     f'{self.get_appt_reason_display()}')
        else:
            title = self.schedule.visits.get(self.visit_code).title
        return title

    @property
    def visit(self):
        """Returns the related visit model instance.
        """
        app_config = django_apps.get_app_config('edc_appointment')
        config = app_config.get_configuration(self._meta.label_lower)
        # attr = app_config.related_visit_model_attrs.get(self._meta.label_lower)
        return getattr(self, config.related_visit_model_attr)

    @property
    def next_by_timepoint(self):
        """Returns the previous appointment or None of all appointments
        for this subject.
        """
        return self.__class__.objects.filter(
            subject_identifier=self.subject_identifier,
            timepoint_datetime__gt=self.timepoint_datetime
        ).order_by('timepoint_datetime').first()

    @property
    def previous_by_timepoint(self):
        """Returns the next appointment or None of all appointments
        for this subject.
        """
        return self.__class__.objects.filter(
            subject_identifier=self.subject_identifier,
            timepoint_datetime__lt=self.timepoint_datetime
        ).order_by('timepoint_datetime').last()

    @property
    def previous(self):
        """Returns the previous appointment or None in this schedule.
        """
        previous_appt = None
        previous_visit = self.schedule.visits.previous(self.visit_code)
        if previous_visit:
            try:
                previous_appt = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit_code=previous_visit.code)
            except ObjectDoesNotExist:
                pass
        return previous_appt

    @property
    def next(self):
        """Returns the next appointment or None in this schedule.
        """
        next_appt = None
        next_visit = self.schedule.visits.next(self.visit_code)
        if next_visit:
            try:
                options = dict(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit_code=next_visit.code)
                next_appt = self.__class__.objects.get(**options)
            except ObjectDoesNotExist:
                pass
        return next_appt

    @property
    def report_datetime(self):
        return self.appt_datetime

    class Meta:
        abstract = True
        unique_together = (
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'visit_code', 'timepoint', 'visit_code_sequence'),
        )
        ordering = ('timepoint_datetime',)
