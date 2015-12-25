from django.db import models
from django.utils import timezone

from edc_base.model.validators import datetime_not_before_study_start, datetime_not_future
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE

from ..choices import YES_NO_DECLINED_COPY


class BaseSpecimenConsent(models.Model):

    """ A base class for a model completed by the user indicating whether a participant has agreed
    for specimens to be stored after study closure."""

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=timezone.now,
        help_text=('If reporting today, use today\'s date/time, otherwise use '
                   'the date/time this information was reported.'))

    version = models.CharField(
        verbose_name='Consent version',
        max_length=10,
        default='?',
        help_text='See \'Consent Type\' for consent versions by period.',
        editable=False,
    )

    purpose_explained = models.CharField(
        verbose_name=("I have explained the purpose of the specimen consent"
                      " to the participant."),
        max_length=15,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,
        help_text="")

    purpose_understood = models.CharField(
        verbose_name=("To the best of my knowledge, the client understands"
                      " the purpose, procedures, risks and benefits of the specimen consent"),
        max_length=15,
        choices=YES_NO_NA,
        null=True,
        blank=False,
        default=NOT_APPLICABLE,)

    offered_copy = models.CharField(
        verbose_name=("I offered the participant a copy of the signed specimen consent and "
                      "the participant accepted the copy"),
        max_length=20,
        choices=YES_NO_DECLINED_COPY,
        null=True,
        blank=False,
        help_text=("If participant declined the copy, return the copy to the clinic to be "
                   "filed with the original specimen consent")
    )

    class Meta:
        abstract = True
