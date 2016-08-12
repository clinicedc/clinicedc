from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from edc_constants.choices import YES_NO_NA
from edc_constants.constants import (
    NEW_APPT, CLOSED, OPEN, IN_PROGRESS, NOT_APPLICABLE)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .choices import APPT_TYPE, APPT_STATUS, COMPLETE_APPT


class TimePointStatusMixin(models.Model):
    """ All completed appointments are noted in this mixin to be inherited by the appointment mixin.

    Only authorized users can access this form. This form allows
    the user to definitely confirm that the appointment has
    been completed"""

    close_datetime = models.DateTimeField(
        verbose_name='Date closed.',
        null=True,
        blank=True)

    time_point_status = models.CharField(
        max_length=15,
        choices=(
            (OPEN, 'Open'),
            ('feedback', 'Feedback'),
            (CLOSED, 'Closed')),
        default=OPEN)

    subject_withdrew = models.CharField(
        verbose_name='Did the participant withdraw consent?',
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        null=True,
        help_text='Use ONLY when subject has changed mind and wishes to withdraw consent')

    reasons_withdrawn = models.CharField(
        verbose_name='Reason participant withdrew consent',
        max_length=35,
        choices=(
            ('changed_mind', 'Subject changed mind'),
            (NOT_APPLICABLE, 'Not applicable')),
        null=True,
        default=NOT_APPLICABLE)

    withdraw_datetime = models.DateTimeField(
        verbose_name='Date and time participant withdrew consent',
        null=True,
        blank=True)

    def get_report_datetime(self):
        return self.close_datetime

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields') or []
        self.validate_status()
        if self.time_point_status == CLOSED and not self.close_datetime:
            self.close_datetime = timezone.now()
        else:
            self.close_datetime = None
        if 'time_point_status' not in update_fields:
            self.time_point_status_open_or_raise()
        super(TimePointStatusMixin, self).save(*args, **kwargs)

    def status_display(self):
        """Formats and returns the status for the dashboard."""
        if self.time_point_status == OPEN:
            return '<span style="color:green;">Open</span>'
        elif self.time_point_status == CLOSED:
            return '<span style="color:red;">Closed</span>'
        elif self.time_point_status == 'feedback':
            return '<span style="color:orange;">Feedback</span>'
    status_display.allow_tags = True

    def validate_status(self, instance=None, exception_cls=None):
        """Closing off only appt that are either done/incomplete/cancelled ONLY."""
        exception_cls = exception_cls or ValidationError
        instance = instance or self
        if instance.time_point_status == CLOSED:
            for appointment in self.get_appointments():
                if appointment.appt_status in [NEW_APPT, IN_PROGRESS]:
                    raise exception_cls(
                        'Cannot close timepoint. Appointment status is {0}.'.format(
                            appointment.appt_status.upper()))

    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    def get_appointments(self):
        return self.appointment_model.objects.filter(pk=self.pk)

    def time_point_status_open_or_raise(self, exception_cls=None):
        """Checks the time point status and prevents edits to the model if
        time_point_status_status == closed."""
        exception_cls = exception_cls or ValidationError
        if self.time_point_status == CLOSED:
            raise ValidationError('Data entry for this time point is closed. See TimePointStatus.')

    @property
    def base_appointment(self):
        return self.appointment_model.objects.get(
            time_point_status__pk=self.pk, visit_code_sequence=0)

    class Meta:
        abstract = True


class AppointmentModelMixin(TimePointStatusMixin):

    """Mixin for the appointment model.

    You must manually add:

        registered_subject = models.ForeignKey(RegisteredSubject)

    Where RegisteredSubject comes from <some_app>.models.

    Only one appointment per subject visit_definition+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    visit_schedule_name = models.CharField(max_length=25, null=True)

    schedule_name = models.CharField(max_length=25, null=True)

    visit_code = models.CharField(max_length=25, null=True)

    #  This identifier is common across a subject's appointment
    appointment_identifier = models.CharField(
        max_length=50,
        blank=True,
        editable=False)

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

    # this is the original calculated appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated appointment datetime. Do not change",
        null=True,
        editable=False)

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

    # TODO: needed????
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
            'Default for subject may be edited Subject Configuration.'))

    def __str__(self):
        return "{0}.{1}".format(
            self.visit_code, self.visit_code_sequence)

    @property
    def visit_definition(self):
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            schedule = visit_schedule.schedules.get(self.schedule_name)
            break
        return schedule.visits.get(self.visit_code)

    class Meta:
        abstract = True


def appointment_model(self):
    return django_apps.get_app_config('edc_appointment').appointment_model


@receiver(post_save, sender=appointment_model)
@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the field is empty."""
    if not raw:
        try:
            if not instance.time_point_status:
                if instance.appt_status == COMPLETE_APPT:
                    instance.time_point_status = CLOSED
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise AttributeError(str(e))
