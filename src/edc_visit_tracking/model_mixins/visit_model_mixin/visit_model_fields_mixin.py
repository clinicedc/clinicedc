from django.db import models
from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future, date_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_constants.constants import YES, ALIVE
from edc_protocol.validators import date_not_before_study_start
from edc_protocol.validators import datetime_not_before_study_start


class VisitModelFieldsMixin(models.Model):
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
        verbose_name='If \'missed\' above, Reason scheduled visit was missed',
        max_length=35,
        blank=True,
        null=True)

    info_source = models.CharField(
        verbose_name='What is the main source of this information?',
        max_length=25)

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

    class Meta:
        abstract = True
