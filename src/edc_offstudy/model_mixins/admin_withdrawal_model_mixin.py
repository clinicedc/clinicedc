from clinicedc_constants import NULL_STRING
from django.db import models

from edc_list_data.utils import get_list_model_app
from edc_model.validators import date_not_future


class AdminWithdrawalModelMixin(models.Model):
    """An End of Study model mixin to collect additional information on
    an administrative withdrawal.

    Set up with form validation where these fields are required if
    `offstudy_reason`== ADMINISTRATIVE_WITHDRAWAL.

    Add a list model, <LIST_MODEL_APP_LABEL>.adminwithdrawalreasons and update
    <LIST_MODEL_APP_LABEL>.list_data.py

        "meta_lists.adminwithdrawalreasons": [
            (NOT_APPLICABLE, "Not applicable"),
            (OTHER, "Other reason (specify below)"),
        ],

    To admin add:

        def get_changeform_initial_data(self, request):
            initial = super().get_changeform_initial_data(request)
            with context.suppress(ObjectDoesNotExist):
                obj = django_apps.get_model(
                    f"{get_list_model_app()}.adminwithdrawalreasons"
                    ).objects.get(name=NOT_APPLICABLE)
                initial.setdefault("admin_withdrawal_reason", obj.pk)
            return initial

    """

    admin_withdrawal_date = models.DateField(
        verbose_name="Date of administrative withdrawal",
        validators=[date_not_future],
        blank=True,
        null=True,
    )

    admin_withdrawal_reason = models.ForeignKey(
        f"{get_list_model_app()}.adminwithdrawalreasons",
        verbose_name=(
            "If the patient was withdrawn for ADMINISTRATIVE reasons, please explain"
        ),
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    admin_withdrawal_reason_other = models.TextField(
        verbose_name="If ADMINISTRATIVE withdrawal for 'other' reason, please specify ...",
        max_length=500,
        blank=True,
        default=NULL_STRING,
    )

    class Meta:
        abstract = True
