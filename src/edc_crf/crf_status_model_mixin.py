from django.conf import settings
from django.db import models
from edc_constants.constants import INCOMPLETE

from .choices import CRF_STATUS

crf_status_default = getattr(settings, "CRF_STATUS_DEFAULT", INCOMPLETE)


class CrfStatusModelMixin(models.Model):
    crf_status = models.CharField(
        verbose_name="CRF status",
        max_length=25,
        choices=CRF_STATUS,
        default=crf_status_default,
        help_text="If some data is still pending, flag this CRF as incomplete",
    )

    crf_status_comments = models.TextField(
        verbose_name="Any comments related to status of this CRF",
        null=True,
        blank=True,
        help_text="for example, why some data is still pending",
    )

    class Meta:
        abstract = True
