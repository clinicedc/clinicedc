from django.db import models

from edc_constants.choices import YES_NO, YES_NO_DECLINED
from edc_consent.models.validators import eligible_if_yes_or_declined


class SampleCollectionFieldsMixin(models.Model):

    may_store_samples = models.CharField(
        verbose_name="Sample storage",
        max_length=3,
        choices=YES_NO,
        help_text=("Does the subject agree to have samples stored after the study has ended")
    )

    consent_copy = models.CharField(
        verbose_name=("I have provided the client with a copy of their signed informed consent"),
        max_length=20,
        choices=YES_NO_DECLINED,
        validators=[eligible_if_yes_or_declined, ],
        null=True,
        blank=False,
        help_text="If declined, return copy to the clinic with the consent",
    )

    class Meta:
        abstract = True
