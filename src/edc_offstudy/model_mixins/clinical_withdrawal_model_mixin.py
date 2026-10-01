from clinicedc_constants import NULL_STRING
from django.db import models

from edc_list_data.utils import get_list_model_app
from edc_model.validators import date_not_future


class ClinicalWithdrawalModelMixin(models.Model):
    """An End of Study model mixin to collect additional information on
    a clinical withdrawal.

    Set up with form validation where these fields are required if
    `offstudy_reason`== CLINICAL_WITHDRAWAL.

    Add a list model, <LIST_MODEL_APP_LABEL>.clinicalwithdrawalreasons and update
    <LIST_MODEL_APP_LABEL>.list_data.py

        "meta_lists.clinicalwithdrawalreasons": [
            (NOT_APPLICABLE, "Not applicable"),
            (OTHER, "Other reason (specify below)"),
        ],

    """

    clinical_withdrawal_date = models.DateField(
        verbose_name="Date of clinical withdrawal",
        validators=[date_not_future],
        blank=True,
        null=True,
    )

    clinical_withdrawal_reason = models.ForeignKey(
        f"{get_list_model_app()}.clinicalwithdrawalreasons",
        verbose_name=(
            "If the patient was withdrawn on CLINICAL grounds, "
            "please specify the PRIMARY reason"
        ),
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    clinical_withdrawal_reason_other = models.TextField(
        verbose_name="If withdrawn for 'other' condition, please explain",
        max_length=500,
        blank=True,
        default=NULL_STRING,
    )

    clinical_withdrawal_investigator_decision = models.TextField(
        verbose_name="If withdrawl was an 'investigator decision', please explain ...",
        max_length=500,
        blank=True,
        default=NULL_STRING,
    )

    class Meta:
        abstract = True
