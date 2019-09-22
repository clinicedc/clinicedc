from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.choices import YES_NO


class AeInitialSaeModelMixin(models.Model):

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

    sae_reason = models.ForeignKey(
        "edc_adverse_event.saereason",
        on_delete=PROTECT,
        verbose_name='If "Yes", reason for SAE:',
        help_text="If subject deceased, submit a Death Report",
        blank=False,
    )

    class Meta:
        abstract = True
