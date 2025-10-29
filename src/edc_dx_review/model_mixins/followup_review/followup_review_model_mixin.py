from clinicedc_constants import NOT_APPLICABLE
from django.db import models

from edc_constants.choices import YES_NO_NA


class FollowupReviewModelMixin(models.Model):
    care_delivery = models.CharField(
        verbose_name=(
            "Was care for this `condition` delivered in an integrated care clinic today?"
        ),
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="Select `not applicable` if site was not selected for integrated care.",
    )

    care_delivery_other = models.TextField(
        verbose_name="If NO, please explain", null=True, blank=True
    )

    class Meta:
        abstract = True
