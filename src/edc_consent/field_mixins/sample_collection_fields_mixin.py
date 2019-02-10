from django.db import models
from edc_constants.choices import YES_NO


class SampleCollectionFieldsMixin(models.Model):

    may_store_genetic_samples = models.CharField(
        verbose_name=(
            "Does the participant agree that a portion of "
            "the blood sample that is taken be stored for genetic "
            "analysis?"
        ),
        max_length=25,
        choices=YES_NO,
    )

    may_store_samples = models.CharField(
        verbose_name=(
            "Does the participant agree to have samples "
            "stored after the study has ended"
        ),
        max_length=3,
        choices=YES_NO,
    )

    class Meta:
        abstract = True
