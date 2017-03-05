import copy

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_appointment.constants import IN_PROGRESS_APPT, COMPLETE_APPT
from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future, date_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import YES, ALIVE
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import (
    datetime_not_before_study_start, date_not_before_study_start)
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from ..choices import VISIT_REASON
from ..constants import (
    FOLLOW_UP_REASONS, REQUIRED_REASONS, NO_FOLLOW_UP_REASONS)

from .previous_visit_model_mixin import PreviousVisitModelMixin
from django.db.models.deletion import PROTECT


class VisitModelMixin(
        VisitScheduleModelMixin, NonUniqueSubjectIdentifierFieldMixin,
        PreviousVisitModelMixin, models.Model):

    """
    For example:

        class SubjectVisit(VisitModelMixin, CreatesMetadataModelMixin,
                           RequiresConsentMixin, BaseUuidModel):

            appointment = models.OneToOneField('Appointment',
                                                on_delete=PROTECT)

        class Meta(VisitModelMixin.Meta):
            app_label = 'my_app'
    """
    report_datetime = models.DateTimeField(
        verbose_name='Visit Date and Time',
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow,
        help_text='Date and time of this report')

    reason = models.CharField(
        verbose_name='What is the reason for this visit?',
        max_length=25,
        help_text=(
            '<Override the field class for this model '
            'field attribute in ModelForm>'))

    study_status = models.CharField(
        verbose_name='What is the participant\'s current study status',
        max_length=50,
        help_text=(
            '<Override the field class for this model field '
            'attribute in ModelForm>'))

    require_crfs = models.CharField(
        max_length=10,
        verbose_name='Are scheduled data being submitted with this visit?',
        choices=YES_NO,
        default=YES)

    reason_missed = models.CharField(
        verbose_name='If \missed\' above, Reason scheduled visit was missed',
        max_length=35,
        blank=True,
        null=True)

    info_source = models.CharField(
        verbose_name='What is the main source of this information?',
        max_length=25,
        help_text='')

    info_source_other = OtherCharField()

    survival_status = models.CharField(
        max_length=10,
        verbose_name='Participant\'s survival status',
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        default=ALIVE)

    last_alive_date = models.DateField(
        verbose_name='Date participant last known alive',
        validators=[date_not_before_study_start, date_not_future],
        null=True,
        blank=True)

    comments = models.TextField(
        verbose_name=(
            'Comment if any additional pertinent information '
            'about the participant'),
        max_length=250,
        blank=True,
        null=True)

    def __str__(self):
        return '{} {}'.format(self.subject_identifier, self.visit_code)

    def save(self, *args, **kwargs):
        if self.__class__.appointment.field.rel.on_delete != PROTECT:
            raise ImproperlyConfigured(
                'OneToOne relation to appointment must set '
                'on_delete=PROTECT. Got {}'.format(
                    self.__class__.appointment.field.rel.on_delete.__name__))
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.schedule_name = self.appointment.schedule_name
        self.visit_code = self.appointment.visit_code
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name,
                self.visit_code)
    # natural_key.dependencies = ['app_label.appointment']

    @property
    def appointment_zero(self):
        appointment_zero = None
        try:
            if self.appointment.visit_instance == '0':
                appointment_zero = self.appointment
        except AttributeError:
            pass
        if not appointment_zero:
            try:
                appointment_zero = self.appointment.__class__.objects.get(
                    subject_identifier=self.appointment.subject_identifier,
                    visit_instance='0')
            except self.appointment.__class__.DoesNotExist:
                pass
        return appointment_zero

    def get_visit_reason_no_follow_up_choices(self):
        """Returns the visit reasons that do not imply any
        data collection; that is, the subject is not available.
        """
        dct = {}
        for item in NO_FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

    def get_visit_reason_follow_up_choices(self):
        """Returns visit reasons that imply data is being collected;
        that is, subject is present.
        """
        dct = {}
        for item in FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

    def get_visit_reason_choices(self):
        """Returns a tuple of the reasons choices for the reason field.
        """
        return VISIT_REASON

    def _check_visit_reason_keys(self):
        user_keys = (
            [k for k in self.get_visit_reason_no_follow_up_choices().iterkeys()]
            + [k for k in self.get_visit_reason_follow_up_choices().iterkeys()])
        default_keys = copy.deepcopy(REQUIRED_REASONS)
        if list(set(default_keys) - set(user_keys)):
            missing_keys = list(set(default_keys) - set(user_keys))
            if missing_keys:
                raise ImproperlyConfigured(
                    'User\'s visit reasons tuple must contain all keys '
                    'for no follow-up {1} and all for follow-up {2}. '
                    'Missing {3}. Override methods \'get_visit_reason_'
                    'no_follow_up_choices\' and \'get_visit_reason_follow_'
                    'up_choices\' on the visit model if you are not using '
                    'the default keys of {4}. Got {0}'.format(
                        user_keys,
                        NO_FOLLOW_UP_REASONS,
                        FOLLOW_UP_REASONS,
                        missing_keys,
                        REQUIRED_REASONS))

    def post_save_check_appointment_in_progress(self):
        if self.reason in self.get_visit_reason_no_follow_up_choices():
            if self.appointment.appt_status != COMPLETE_APPT:
                self.appointment.appt_status = COMPLETE_APPT
                self.appointment.save()
        else:
            if self.appointment.appt_status != IN_PROGRESS_APPT:
                self.appointment.appt_status = IN_PROGRESS_APPT
                self.appointment.save()

    class Meta:
        abstract = True
        unique_together = (
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'visit_code'),
            ('subject_identifier', 'visit_schedule_name',
             'schedule_name', 'report_datetime'),
        )
        ordering = (('subject_identifier', 'visit_schedule_name',
                     'schedule_name', 'visit_code', 'report_datetime', ))
