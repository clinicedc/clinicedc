from django.db import models
from edc_constants.choices import YES_NO, YES_NO_DECLINED

from ..validators import eligible_if_yes, eligible_if_yes_or_declined


class ReviewFieldsMixin(models.Model):

    consent_reviewed = models.CharField(
        verbose_name="I have reviewed the consent with the participant",
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, participant is not eligible.",
    )

    study_questions = models.CharField(
        verbose_name=(
            "I have answered all questions the participant had about the study"
        ),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, participant is not eligible.",
    )

    assessment_score = models.CharField(
        verbose_name=(
            "I have asked the participant questions about this study and "
            "the participant has demonstrated understanding"
        ),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, participant is not eligible.",
    )

    consent_signature = models.CharField(
        verbose_name=(
            "I have verified that the participant has signed the consent form"
        ),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, participant is not eligible.",
    )

    consent_copy = models.CharField(
        verbose_name=(
            "I have provided the participant with a copy of their "
            "signed informed consent"
        ),
        max_length=20,
        choices=YES_NO_DECLINED,
        validators=[eligible_if_yes_or_declined],
        null=True,
        blank=False,
        help_text="If declined, return copy with the consent",
    )

    class Meta:
        abstract = True
