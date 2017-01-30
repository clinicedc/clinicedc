from django.db import models

from edc_constants.choices import YES_NO


class SampleCollectionFieldsMixin(models.Model):

    may_store_samples = models.CharField(
        verbose_name=(
            'Does the subject agree to have samples '
            'stored after the study has ended'),
        max_length=3,
        choices=YES_NO,
    )

    class Meta:
        abstract = True
