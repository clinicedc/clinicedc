from django.db import models
from edc_constants.choices import YES_NO


class ClinicalReviewModelMixin(models.Model):

    complications = models.CharField(
        verbose_name="Since last seen, has the patient had any complications",
        max_length=15,
        choices=YES_NO,
        help_text="If Yes, complete the `Complications` CRF",
    )

    class Meta:
        abstract = True
        verbose_name = "Clinical Review"
        verbose_name_plural = "Clinical Review"
