import copy

import django.db.models.options as options

from django.apps import apps as django_apps
from django.db import models, transaction
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields.related import OneToOneField, ForeignKey

from edc_appointment.constants import IN_PROGRESS_APPT, COMPLETE_APPT
from edc_base.model.fields.custom_fields import OtherCharField
from edc_base.model.validators.date import datetime_not_future, date_not_future
from edc_protocol.validators import datetime_not_before_study_start, date_not_before_study_start
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import YES, ALIVE
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.managers import CrfModelManager

from .choices import VISIT_REASON
from .constants import FOLLOW_UP_REASONS, REQUIRED_REASONS, NO_FOLLOW_UP_REASONS


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('crf_inline_parent_model',)


class PreviousVisitError(Exception):
    pass


class CrfModelMixin(models.Model):

    """Base mixin for all CRF models.

    You need to define the visit model foreign_key, e.g:

        subject_visit = models.ForeignKey(SubjectVisit)

    """

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=timezone.now,
        help_text=('If reporting today, use today\'s date/time, otherwise use '
                   'the date/time this information was reported.'))

    objects = CrfModelManager()

    def __str__(self):
        return str(self.get_visit())

#     def save(self, *args, **kwargs):
#         self.get_visit().appointment.time_point_status_open_or_raise()
#         super(CrfModelMixin, self).save(*args, **kwargs)

    @property
    def visit_model(self):
        app_config = django_apps.get_app_config('edc_visit_tracking')
        return app_config.visit_model(self._meta.app_label)

    @property
    def visit_model_attr(self):
        app_config = django_apps.get_app_config('edc_visit_tracking')
        return app_config.visit_model_attr(self._meta.label_lower)

    def get_visit(self):
        return getattr(self, self.visit_model_attr)

    def natural_key(self):
        return (getattr(self, self.visit_model_attr).natural_key(), )
    # TODO: need to add the natural key dependencies !!

    def get_subject_identifier(self):
        return self.get_visit().appointment.subject_identifier

    def get_report_datetime(self):
        return self.report_datetime

    def dashboard(self):
        url = reverse(
            'subject_dashboard_url',
            kwargs={'dashboard_model': 'appointment',
                    'dashboard_id': self.get_visit().appointment.pk,
                    'show': 'appointments'})
        return """<a href="{url}" />dashboard</a>""".format(url=url)
    dashboard.allow_tags = True

    class Meta:
        abstract = True


class CrfInlineModelMixin(models.Model):
    """A mixin for models used as inlines in ModelAdmin."""

    def __init__(self, *args, **kwargs):
        """Try to detect the inline parent model attribute name or raise,"""
        super(CrfInlineModelMixin, self).__init__(*args, **kwargs)
        try:
            self._meta.crf_inline_parent_model
        except AttributeError:
            fks = [field for field in self._meta.fields if isinstance(field, (OneToOneField, ForeignKey))]
            if len(fks) == 1:
                self.__class__._meta.crf_inline_parent_model = fks[0].name
            else:
                raise ImproperlyConfigured(
                    'CrfInlineModelMixin cannot determine the inline parent model name. '
                    'Got more than one foreign key. Try declaring \"crf_inline_parent_model = \'<field name>\'\" '
                    'explicitly in Meta.')

    def __str__(self):
        return str(self.parent_instance.get_visit())

    def natural_key(self):
        return self.get_visit().natural_key()

    @property
    def parent_instance(self):
        """Return the instance of the inline parent model."""
        return getattr(self, self._meta.crf_inline_parent_model)

    @property
    def parent_model(self):
        """Return the class of the inline parent model."""
        return getattr(self.__class__, self._meta.crf_inline_parent_model).field.rel.to

    def get_visit(self):
        """Return the instance of the inline parent model's visit model."""
        return getattr(self.parent_instance, self.parent_model.visit_model_attr)

    def get_report_datetime(self):
        return self.get_visit().get_report_datetime()

    def get_subject_identifier(self):
        return self.get_visit().get_subject_identifier()

    class Meta:
        crf_inline_parent_model = None  # foreign key attribute that relates this model to the parent model
        abstract = True


class PreviousVisitModelMixin(models.Model):

    """A model mixin to force the user to complete visits in sequence.

    * Ensures the previous visit exists before allowing save() by raising PreviousVisitError.
    * If the visit is the first in the sequence, save() is allowed.
    * If 'requires_previous_visit' = False, mixin is disabled.

    ...note: Review the value of \'time_point\' and \'base_interval\' from VisitDefintion
        to confirm the visits are in order. This mixin assumes ordering VisitDefinition
        by 'time_point' and 'base_interval' gives the correct visit code sequence.
        Also assumes visits are grouped by the visit tracking form and the \'group\' attr.

    For example:

        class TestVisit(MetaDataMixin, PreviousVisitModelMixin, VisitModelMixin):

            class Meta:
                app_label = 'my_app'

    """

    requires_previous_visit = True

    def save(self, *args, **kwargs):
        self.has_previous_visit_or_raise()
        super(PreviousVisitModelMixin, self).save(*args, **kwargs)

    def has_previous_visit_or_raise(self, exception_cls=None):
        """Returns True if the previous visit in the schedule exists or this is the first visit.

        Is by-passed if 'requires_previous_visit' is False.

        You can call this from the forms clean() method."""
        exception_cls = exception_cls or PreviousVisitError
        if self.requires_previous_visit:
            previous_visit_definition = self.previous_visit_definition(
                self.appointment.visit_schedule_name, self.appointment.visit_code)
            if previous_visit_definition:
                if self.previous_visit(previous_visit_definition):
                    has_previous_visit = True
                elif (self.appointment.visit_definition.time_point == 0 and
                        self.appointment.visit_definition.base_interval == 0):
                    has_previous_visit = True
                else:
                    has_previous_visit = False
                if not has_previous_visit:
                    self.appointment.__class__.objects.filter(subject_identifier=self.appointment.subject_identifier)
                    raise exception_cls(
                        'Previous visit report for \'{}\' is not complete.'.format(previous_visit_definition.code))

    def previous_visit_definition(self, schedule_name, visit_code):
        """Returns the previous visit definition relative to this instance or None.

        Only selects visit definition instances for this visit model."""
        visit_schedule = site_visit_schedules.get_visit_schedule(self.appointment.visit_schedule_name)
        schedule = visit_schedule.schedules.get(self.appointment.schedule_name)
        return schedule.get_previous_visit(visit_code)

    def previous_visit(self, previous_visit_definition=None):
        """Returns the previous visit if it exists."""
        with transaction.atomic():
            try:
                previous_visit_definition = previous_visit_definition or self.previous_visit_definition(
                    self.appointment.schedule_name, self.appointment.visit_code)
                previous_visit = self.__class__.objects.get(
                    appointment__subject_identifier=self.appointment.subject_identifier)
            except self.__class__.DoesNotExist:
                previous_visit = None
            except self.__class__.MultipleObjectsReturned:
                previous_appointment = self.appointment.__class__.objects.filter(
                    subject_identifier=self.appointment.subject_identifier).order_by('-visit_instance')[0]
                previous_visit = self.__class__.objects.filter(
                    appointment=previous_appointment)
        return previous_visit

    class Meta:
        abstract = True


class VisitModelMixin(models.Model):

    """
    For example:

        class SubjectVisit(MetaDataMixin, PreviousVisitModelMixin, VisitModelMixin, BaseUuidModel):

            appointment = models.OneToOneField(MyAppointmentModel)

        class Meta:
            app_label = 'my_app'

    """

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

    def __str__(self):
        return '{} {}'.format(self.subject_identifier, self.appointment.visit_code)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.appointment.subject_identifier
        super(VisitModelMixin, self).save(*args, **kwargs)

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
        data collection; that is, the subject is not available."""
        dct = {}
        for item in NO_FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

#     def get_off_study_reason(self):
#         return (app_config.lost, COMPLETED_PROTOCOL_VISIT)

    def get_visit_reason_follow_up_choices(self):
        """Returns visit reasons that imply data is being collected; that is, subject is present."""
        dct = {}
        for item in FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

    def get_visit_reason_choices(self):
        """Returns a tuple of the reasons choices for the reason field."""
        return VISIT_REASON

    def _check_visit_reason_keys(self):
        user_keys = ([k for k in self.get_visit_reason_no_follow_up_choices().iterkeys()] +
                     [k for k in self.get_visit_reason_follow_up_choices().iterkeys()])
        default_keys = copy.deepcopy(REQUIRED_REASONS)
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

    def get_report_datetime(self):
        return self.report_datetime

    class Meta:
        abstract = True


class CaretakerFieldsMixin(models.Model):
    """A fields mixin for visit models where information on the the participant is offered by
    another person, as in the case of infant and mother.

    One the ModelForm, override the default form to customize the choices and labels.

    """
    information_provider = models.CharField(
        verbose_name="Please indicate who provided most of the information for this participant's visit",
        max_length=20)

    information_provider_other = models.CharField(
        verbose_name="if information provider is Other, please specify",
        max_length=20,
        blank=True,
        null=True)

    is_present = models.CharField(
        max_length=10,
        verbose_name="Is the participant present at today\'s visit",
        choices=YES_NO,
        default=YES)

    class Meta:
        abstract = True
