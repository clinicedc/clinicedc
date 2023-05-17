from django.db import models
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE


class CitizenFieldsMixin(models.Model):
    citizen = models.CharField(
        verbose_name="Is the participant a Botswana citizen? ",
        max_length=3,
        choices=YES_NO,
    )

    legal_marriage = models.CharField(
        verbose_name=(
            "If not a citizen, is the participant " "legally married to a Botswana citizen?"
        ),
        max_length=3,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        null=True,
        blank=False,
        help_text="If 'No', participant may not be consented.",
    )

    marriage_certificate = models.CharField(
        verbose_name=(
            "[Interviewer] Has the participant produced the marriage " "certificate as proof? "
        ),
        max_length=3,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        null=True,
        blank=False,
        help_text="If 'No', participant may not be consented.",
    )

    marriage_certificate_no = models.CharField(
        verbose_name="What is the marriage certificate number?",
        max_length=9,
        null=True,
        blank=True,
        help_text="e.g. 000/YYYY",
    )

    class Meta:
        abstract = True
