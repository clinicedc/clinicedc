from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_constants.choices import DOCUMENT_STATUS
from edc_constants.constants import INCOMPLETE

from ..update_crf_status_for_instance import update_crf_status_for_instance


def get_crf_status_default():
    return getattr(settings, "CRF_STATUS_DEFAULT", INCOMPLETE)


class CrfStatusModelMixin(models.Model):
    """A model mixin that adds CRF status fields and
    a method to update the status.

    The method is called in an edc_crf signal.
    """

    crf_status = models.CharField(
        verbose_name="CRF status",
        max_length=25,
        choices=DOCUMENT_STATUS,
        default=get_crf_status_default,
        help_text=_("If some data is still pending, flag this CRF as incomplete"),
    )

    crf_status_comments = models.TextField(
        verbose_name=_("Any comments related to status of this CRF"),
        null=True,
        blank=True,
        help_text=_("for example, why some data is still pending"),
    )

    def update_crf_status_for_instance(self):
        return update_crf_status_for_instance(self)

    class Meta:
        abstract = True
