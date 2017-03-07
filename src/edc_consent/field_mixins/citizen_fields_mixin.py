from django.db import models

from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE


class CitizenFieldsMixin(models.Model):

    citizen = models.CharField(
        verbose_name='Are you a Botswana citizen? ',
        max_length=3,
        choices=YES_NO,
        help_text='',
    )

    legal_marriage = models.CharField(
        verbose_name=(
            'If not a citizen, are you legally married to a Botswana Citizen?'),
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='If \'NO\' participant will not be enrolled.',
    )

    marriage_certificate = models.CharField(
        verbose_name=(
            '[Interviewer] Has the participant produced the marriage '
            'certificate, as proof? '),
        max_length=3,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text='If \'NO\' participant will not be enrolled.',
    )

    marriage_certificate_no = models.CharField(
        verbose_name=('What is the marriage certificate number?'),
        max_length=9,
        null=True,
        blank=True,
        help_text='e.g. 000/YYYY',
    )

    class Meta:
        abstract = True
