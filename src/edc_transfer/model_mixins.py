from django.conf import settings
from django.db import models
from django_crypto_fields.fields import EncryptedTextField
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO, YES_NO_UNSURE
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin
from edc_utils import convert_php_dateformat
from edc_utils.date import get_utcnow

from .choices import TRANSFER_INITIATORS
from .constants import SUBJECT_TRANSFER_ACTION


class SubjectTransferModelMixin(
    SiteModelMixin,
    ActionModelMixin,
    UniqueSubjectIdentifierFieldMixin,
    models.Model,
):
    action_name = SUBJECT_TRANSFER_ACTION

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    transfer_date = models.DateField(verbose_name="Transfer date", default=get_utcnow)

    initiated_by = models.CharField(
        verbose_name="Who initiated the transfer request",
        max_length=25,
        choices=TRANSFER_INITIATORS,
    )

    initiated_by_other = edc_models.OtherCharField()

    transfer_reason = models.ManyToManyField(
        f"{settings.LIST_MODEL_APP_LABEL}.transferreasons",
        verbose_name="Reason for transfer",
    )

    transfer_reason_other = edc_models.OtherCharField()

    may_return = models.CharField(
        verbose_name=(
            "Is the participant likely to transfer back before "
            "the end of their stay in the trial?"
        ),
        max_length=15,
        choices=YES_NO_UNSURE,
    )

    may_contact = models.CharField(
        verbose_name="Is the participant willing to be contacted at the end of the study?",
        max_length=15,
        choices=YES_NO,
    )

    comment = EncryptedTextField(verbose_name="Additional Comments")

    def __str__(self):
        transfer_date = "???"
        if self.transfer_date:
            transfer_date = self.transfer_date.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
        return f"{self.subject_identifier} on {transfer_date}."

    def natural_key(self):
        return (self.subject_identifier,)  # noqa

    class Meta:
        abstract = True
        verbose_name = "Subject Transfer"
        verbose_name_plural = "Subject Transfers"
