from django.db import models
from edc_constants.choices import DOCUMENT_STATUS

from . import crf_status_default
from .update_crf_status_for_instance import update_crf_status_for_instance


class CrfStatusModelMixin(models.Model):
    crf_status = models.CharField(
        verbose_name="CRF status",
        max_length=25,
        choices=DOCUMENT_STATUS,
        default=crf_status_default,
        help_text="If some data is still pending, flag this CRF as incomplete",
    )

    crf_status_comments = models.TextField(
        verbose_name="Any comments related to status of this CRF",
        null=True,
        blank=True,
        help_text="for example, why some data is still pending",
    )

    def update_crf_status_for_instance(self):
        return update_crf_status_for_instance(self)

    class Meta:
        abstract = True
