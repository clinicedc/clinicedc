from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE

from ..choices import SAE_REASONS


class SaeModelMixin(models.Model):

    sae = models.CharField(
        verbose_name="Is this event a SAE?",
        max_length=5,
        choices=YES_NO,
        help_text=(
            "(i.e. results in death, in-patient "
            "hospitalisation/prolongation, significant disability or is "
            "life-threatening)"
        ),
    )

    sae_reason = models.CharField(
        verbose_name='If "Yes", reason for SAE:',
        max_length=50,
        choices=SAE_REASONS,
        default=NOT_APPLICABLE,
        help_text="If subject deceased, submit a Death Report",
    )

    #     sae_reason = models.ForeignKey(
    #          "edc_adverse_event.saereason",
    #         verbose_name='If "Yes", reason for SAE:',
    #         default=NOT_APPLICABLE,
    #         help_text="If subject deceased, submit a Death Report",
    #     )

    #     def save(self, *args, **kwargs):
    #         if not self.sae_reason:
    #             self.sae_reason = SaeReason.objects.get(short_name=NOT_APPLICABLE)
    #         super().save(*args, **kwargs)

    class Meta:
        abstract = True
