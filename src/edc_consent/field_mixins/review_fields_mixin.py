from django.db import models

from edc_consent.validators import eligible_if_yes, eligible_if_yes_or_declined
from edc_constants.choices import YES_NO, YES_NO_DECLINED


class ReviewFieldsMixin(models.Model):

    consent_reviewed = models.CharField(
        verbose_name='I have reviewed the consent with the client',
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes, ],
        null=True,
        blank=False,
        help_text='If no, INELIGIBLE',
    )
    study_questions = models.CharField(
        verbose_name=(
            'I have answered all questions the client had about the study'),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes, ],
        null=True,
        blank=False,
        help_text='If no, INELIGIBLE',
    )
    assessment_score = models.CharField(
        verbose_name=(
            'I have asked the client questions about this study and '
            'they have demonstrated understanding'),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes, ],
        null=True,
        blank=False,
        help_text='If no, INELIGIBLE',
    )

    consent_signature = models.CharField(
        verbose_name=('The client has signed the consent form?'),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes, ],
        null=True,
        blank=False,
        # default='Yes',
        help_text='If no, INELIGIBLE',
    )

    consent_copy = models.CharField(
        verbose_name=(
            'I have provided the client with a copy of their '
            'signed informed consent'),
        max_length=20,
        choices=YES_NO_DECLINED,
        validators=[eligible_if_yes_or_declined, ],
        null=True,
        blank=False,
        help_text='If declined, return copy to the clinic with the consent',
    )

    class Meta:
        abstract = True
