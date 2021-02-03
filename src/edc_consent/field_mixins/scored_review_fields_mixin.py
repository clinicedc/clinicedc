from django.db import models
from edc_constants.choices import YES_NO, YES_NO_DECLINED

from ..validators import eligible_if_yes


class ScoredReviewFieldsMixin(models.Model):

    consent_reviewed = models.CharField(
        verbose_name="I have reviewed the consent with the client",
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, INELIGIBLE",
    )

    study_questions = models.CharField(
        verbose_name="I have answered all questions the client had about the study",
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, INELIGIBLE",
    )

    assessment_score = models.CharField(
        # TODO: i have asked the client questions about this study
        # and they have demonstrated understanding
        verbose_name=(
            "The client has completed the assessment of understanding with a" " passing score"
        ),
        max_length=3,
        choices=YES_NO,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text="If no, INELIGIBLE",
    )

    consent_copy = models.CharField(
        verbose_name=(
            "I have provided the client with a copy of their signed informed" " edc_consent"
        ),
        max_length=3,
        choices=YES_NO_DECLINED,
        validators=[eligible_if_yes],
        null=True,
        blank=False,
        help_text=(
            "If no, INELIGIBLE. If declined, return copy to the " "clinic with the edc_consent"
        ),
    )

    class Meta:
        abstract = True
