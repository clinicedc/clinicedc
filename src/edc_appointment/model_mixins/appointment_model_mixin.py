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
        help_text='timepoint from schedule')

    timepoint_datetime = models.DateTimeField(
        null=True,
        help_text='Unadjusted datetime calculated from visit schedule')

    appt_close_datetime = models.DateTimeField(
        null=True,
        help_text=(
            'timepoint_datetime adjusted according to the nearest '
            'available datetime for this facility'))

    facility_name = models.CharField(
        max_length=25,
        help_text='set by model that creates appointments, e.g. Enrollment')

    appt_datetime = models.DateTimeField(
        verbose_name=('Appointment date and time'),
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
        choices=APPT_REASON)

    comment = models.CharField(
        'Comment',
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    objects = AppointmentManager()

    def __str__(self):
        return f'{self.visit_code}.{self.visit_code_sequence}'

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
        return getattr(self, self.related_visit_model_attr())

    @classmethod
    def related_visit_model_attr(cls):
        app_config = django_apps.get_app_config('edc_appointment')
        appointment_config = app_config.get_configuration(
            name=cls._meta.label_lower)
        return appointment_config.related_visit_model_attr

    @classmethod
    def visit_model_cls(cls):
        return getattr(cls, cls.related_visit_model_attr()).related.related_model

    @property
    def next_by_timepoint(self):
        """Returns the previous appointment or None of all appointments
        for this subject for visit_code_sequence=0.
        """
        return self.__class__.objects.filter(
            subject_identifier=self.subject_identifier,
            timepoint__gt=self.timepoint,
            visit_code_sequence=0
        ).order_by('timepoint').first()

    @property
    def last_visit_code_sequence(self):
        """Returns an integer, or None, that is the visit_code_sequence
        of the last appointment for this visit code that is not self.
        (ordered by visit_code_sequence).

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        obj = self.__class__.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            visit_code_sequence__gt=self.visit_code_sequence
        ).order_by('visit_code_sequence').last()
        if obj:
            return obj.visit_code_sequence
        return None

    @property
    def next_visit_code_sequence(self):
        """Returns an integer that is the next visit_code_sequence.

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        if self.last_visit_code_sequence:
            return self.last_visit_code_sequence + 1
        return self.visit_code_sequence + 1

    @property
    def previous_by_timepoint(self):
        """Returns the previous appointment or None by timepoint
        for visit_code_sequence=0.
        """
        return self.__class__.objects.filter(
            subject_identifier=self.subject_identifier,
            timepoint__lt=self.timepoint,
            visit_code_sequence=0
        ).order_by('timepoint').last()

    @property
    def previous(self):
        """Returns the previous appointment or None in this schedule
        for visit_code_sequence=0.
        """
        previous_appt = None
        previous_visit = self.schedule.visits.previous(self.visit_code)
        if previous_visit:
            try:
                previous_appt = self.__class__.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit_code=previous_visit.code,
                    visit_code_sequence=0)
            except ObjectDoesNotExist:
                pass
        return previous_appt

    @property
    def next(self):
        """Returns the next appointment or None in this schedule
        for visit_code_sequence=0.
        """
        next_appt = None
        next_visit = self.schedule.visits.next(self.visit_code)
        if next_visit:
            try:
                options = dict(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit_code=next_visit.code,
                    visit_code_sequence=0)
                next_appt = self.__class__.objects.get(**options)
            except ObjectDoesNotExist:
                pass
        return next_appt

    @property
    def facility(self):
        """Returns the facility instance for this facility name.
        """
        app_config = django_apps.get_app_config('edc_facility')
        return app_config.get_facility(name=self.facility_name)

    @property
    def report_datetime(self):
        return self.appt_datetime

    class Meta:
        abstract = True
        unique_together = (
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'visit_code', 'timepoint', 'visit_code_sequence'),
        )
        ordering = ('timepoint', 'visit_code_sequence')
