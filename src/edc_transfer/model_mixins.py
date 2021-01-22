from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model import models as edc_models
from edc_model.models import HistoricalRecords
from edc_sites.models import SiteModelMixin, CurrentSiteManager
from edc_utils.date import get_utcnow

from .choices import TRANSFER_REASONS

"""
Was the transfer related to a worsening condition?

Was the transfer related to drug supply

Was the transfer for financial reasons

Was the transfer because of stigma

In general, did the patient like integrated care
"""


class SubjectTransferModelMixin(
    UniqueSubjectIdentifierFieldMixin, SiteModelMixin, models.Model,
):

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    transfer_date = models.DateField(verbose_name="Transfer date", default=get_utcnow)

    transfer_reason = models.CharField(
        verbose_name="Reason for transfer", max_length=25, choices=TRANSFER_REASONS,
    )

    transfer_reason_other = edc_models.OtherCharField()

    comment = EncryptedTextField(verbose_name="Additional Comments")

    on_site = CurrentSiteManager()
    objects = SubjectIdentifierManager()
    history = HistoricalRecords(inherit=True)

    def natural_key(self):
        return (self.subject_identifier,)

    class Meta:
        abstract = True
        verbose_name = "Subject Transfer"
        verbose_name_plural = "Subject Transfers"
