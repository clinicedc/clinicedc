import copy

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_appointment.models import Appointment
from edc_base.model.fields import OtherCharField
from edc_base.model.validators import datetime_not_before_study_start, datetime_not_future
from edc_base.model.validators.date import date_not_before_study_start, date_not_future
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import IN_PROGRESS, COMPLETE_APPT, LOST_VISIT, YES, ALIVE, COMPLETED_PROTOCOL_VISIT

from ..choices import VISIT_REASON
from ..constants import (
    VISIT_REASON_REQUIRED_CHOICES,
    VISIT_REASON_NO_FOLLOW_UP_CHOICES,
    VISIT_REASON_FOLLOW_UP_CHOICES)
from ..managers import VisitManager


class VisitModelMixin (models.Model):

    """Base model for Appt/Visit Tracking (AF002).

    For entry, requires an appointment be created first, so there
    is no direct reference to 'registered subject' in this model except
    thru appointment.

    List of appointments in admin.py should be limited to scheduled
    appointments for the current registered subject.

    Other ideas: ADD should only allow 'scheduled', and CHANGE only allow 'seen'
    Admin should change the status after ADD.

    As each study will have variations on the 'reason' choices, allow this
    tuple to be defined at the form level. In the ModelForm add something
    like this:

        reason = forms.ChoiceField(
            label = 'Reason for visit',
            choices = [ choice for choice in VISIT_REASON ],
            help_text = ("If 'unscheduled', information is usually reported
                at the next scheduled visit, but exceptions may arise"),
            widget=AdminRadioSelect(renderer=AdminRadioFieldRenderer),
            )

        where the choices tuple is defined in the local app.

    Same for info_source. Something like this:

        info_source = forms.ChoiceField(
            label = 'Source of information',
            choices = [ choice for choice in VISIT_INFO_SOURCE ],
            widget=AdminRadioSelect(renderer=AdminRadioFieldRenderer),
            )

    """

    consent_model = None

    appointment = models.OneToOneField(Appointment)

    report_datetime = models.DateTimeField(
        verbose_name="Visit Date and Time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        help_text='Date and time of this report')

    reason = models.CharField(
        verbose_name="What is the reason for this visit?",
        max_length=25,
        help_text="<Override the field class for this model field attribute in ModelForm>")

    study_status = models.CharField(
        verbose_name="What is the participant's current study status",
        max_length=50,
        help_text="<Override the field class for this model field attribute in ModelForm>")

    require_crfs = models.CharField(
        max_length=10,
        verbose_name='Are scheduled data being submitted with this visit?',
        choices=YES_NO,
        default=YES)

    reason_missed = models.CharField(
        verbose_name="If 'missed' above, Reason scheduled visit was missed",
        max_length=35,
        blank=True,
        null=True)

    info_source = models.CharField(
        verbose_name="What is the main source of this information?",
        max_length=25,
        help_text="")

    info_source_other = OtherCharField()

    survival_status = models.CharField(
        max_length=10,
        verbose_name="Participant\'s survival status",
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        default=ALIVE)

    last_alive_date = models.DateField(
        verbose_name="Date participant last known alive",
        validators=[date_not_before_study_start, date_not_future],
        null=True,
        blank=True)

    comments = models.TextField(
        verbose_name="Comment if any additional pertinent information about the participant",
        max_length=250,
        blank=True,
        null=True,
    )

    subject_identifier = models.CharField(
        verbose_name='subject_identifier',
        max_length=50,
        editable=False,
        help_text='updated automatically as a convenience to avoid sql joins')

    objects = VisitManager()

    def __unicode__(self):
        return unicode(self.appointment)

    def save(self, *args, **kwargs):
        if self.id and not self.byass_time_point_status():
            self.appointment.time_point_status_open_or_raise()
        self.subject_identifier = self.get_subject_identifier()
        super(VisitModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.report_datetime, ) + self.appointment.natural_key()
    natural_key.dependencies = ['edc_appointment.appointment', ]

    def byass_time_point_status(self):
        """Returns False by default but if overridden and set to return
        True, the TimePointStatus instance will not be checked in the save
        method.

        This does not effect the call from the ModelForm."""
        return False

    def get_visit_reason_no_follow_up_choices(self):
        """Returns the visit reasons that do not imply any
        data collection; that is, the subject is not available."""
        dct = {}
        for item in VISIT_REASON_NO_FOLLOW_UP_CHOICES:
            dct.update({item: item})
        return dct

    def get_off_study_reason(self):
        return (LOST_VISIT, COMPLETED_PROTOCOL_VISIT)

    def get_visit_reason_follow_up_choices(self):
        """Returns visit reasons that imply data is being collected; that is, subject is present."""
        dct = {}
        for item in VISIT_REASON_FOLLOW_UP_CHOICES:
            dct.update({item: item})
        return dct

    def get_visit_reason_choices(self):
        """Returns a tuple of the reasons choices for the reason field."""
        return VISIT_REASON

    def _check_visit_reason_keys(self):
        user_keys = ([k for k in self.get_visit_reason_no_follow_up_choices().iterkeys()] +
                     [k for k in self.get_visit_reason_follow_up_choices().iterkeys()])
        default_keys = copy.deepcopy(VISIT_REASON_REQUIRED_CHOICES)
        if list(set(default_keys) - set(user_keys)):
            missing_keys = list(set(default_keys) - set(user_keys))
            if missing_keys:
                raise ImproperlyConfigured(
                    'User\'s visit reasons tuple must contain all keys for no follow-up '
                    '{1} and all for follow-up {2}. Missing {3}. '
                    'Override methods \'get_visit_reason_no_follow_up_choices\' and '
                    '\'get_visit_reason_follow_up_choices\' on the visit model '
                    'if you are not using the default keys of {4}. '
                    'Got {0}'.format(
                        user_keys,
                        VISIT_REASON_NO_FOLLOW_UP_CHOICES,
                        VISIT_REASON_FOLLOW_UP_CHOICES,
                        missing_keys,
                        VISIT_REASON_REQUIRED_CHOICES))

    def post_save_check_in_progress(self):
        if self.reason in self.get_visit_reason_no_follow_up_choices():
            if self.appointment.appt_status != COMPLETE_APPT:
                self.appointment.appt_status = COMPLETE_APPT
                self.appointment.save()
        else:
            if self.appointment.appt_status != IN_PROGRESS:
                self.appointment.appt_status = IN_PROGRESS
                self.appointment.save()

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def get_report_datetime(self):
        return self.report_datetime

    def get_subject_type(self):
        return self.appointment.registered_subject.subject_type

    class Meta:
        abstract = True
