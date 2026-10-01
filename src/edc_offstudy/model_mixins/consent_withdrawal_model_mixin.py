from clinicedc_constants import NOT_APPLICABLE, NULL_STRING
from clinicedc_constants.choices import YES_NO_NA
from django.db import models

from edc_list_data.utils import get_list_model_app
from edc_model.validators import date_not_future


class ConsentWithdrawalModelMixin(models.Model):
    """An End of Study model mixin to collect additional information on
    a consent withdrawal.

    Set up with form validation where these fields are required if
    `offstudy_reason`== CONSENT_WITHDRAWAL.

    Add a list model, <LIST_MODEL_APP_LABEL>.consentwithdrawalreasons and update
    <LIST_MODEL_APP_LABEL>.list_data.py

        "meta_lists.consentwithdrawalreasons": [
            (NOT_APPLICABLE, "Not applicable"),
            (OTHER, "Other reason (specify below)"),
        ],
    """

    consent_withdrawal_date = models.DateField(
        verbose_name="Date consent withdrawn",
        validators=[date_not_future],
        blank=True,
        null=True,
    )

    consent_withdrawal_inperson = models.CharField(
        verbose_name="Did the subject withdraw consent in-person",
        max_length=15,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    consent_withdrawal_reason = models.ForeignKey(
        f"{get_list_model_app()}.consentwithdrawalreasons",
        verbose_name="Specify the PRIMARY reason the patient withdrew consent",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    consent_withdrawal_reason_other = models.TextField(
        verbose_name="If patient withdrew consent for 'other' reason, please specify ...",
        max_length=500,
        blank=True,
        default=NULL_STRING,
    )

    class Meta:
        abstract = True
