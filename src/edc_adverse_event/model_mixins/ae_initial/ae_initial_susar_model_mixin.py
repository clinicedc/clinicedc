from django.db import models
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE


class AeInitialSusarModelMixin(models.Model):

    """This model mixin is for the AE Initial."""

    susar = models.CharField(
        verbose_name="Is this a Suspected Unexpected Serious Adverse Reaction (SUSAR)?",
        choices=YES_NO,
        max_length=5,
        help_text=(
            "If yes, SUSAR must be reported to Principal " "Investigator and TMG immediately,"
        ),
    )

    susar_reported = models.CharField(
        verbose_name="Is SUSAR reported?",
        max_length=5,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    class Meta:
        abstract = True
