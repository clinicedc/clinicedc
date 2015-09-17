from django.db import models
from django.utils.translation import ugettext_lazy as _
from edc_constants.choices import YES_NO


class SampleCollectionFieldsMixin(models.Model):

    may_store_samples = models.CharField(
        verbose_name="Sample storage",
        max_length=3,
        choices=YES_NO,
        help_text=("Does the subject agree to have samples stored after the study has ended")
    )

    class Meta:
        abstract = True
