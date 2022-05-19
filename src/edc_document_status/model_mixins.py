from django.db import models
from edc_constants.choices import DOCUMENT_STATUS
from edc_constants.constants import COMPLETE


class DocumentStatusModelMixin(models.Model):

    document_status = models.CharField(
        verbose_name="Document status",
        max_length=25,
        choices=DOCUMENT_STATUS,
        default=COMPLETE,
        help_text="If some data is still pending, flag as incomplete",
    )

    class Meta:
        abstract = True
