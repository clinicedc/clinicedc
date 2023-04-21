from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE, YES
from edc_model.models import DurationYMDField
from edc_model.validators import date_not_future

from .calculate_date import update_calculated_date


def rx_initial_review_model_mixin_factory(
    fld_prefix: str | None = None, verbose_name_label: str | None = None
):
    fld_prefix = fld_prefix or "rx_init"

    class AbstractModel(models.Model):
        def save(self, *args, **kwargs):
            update_calculated_date(
                self, fld_prefix=fld_prefix, reference_field="report_datetime"
            )
            super().save(*args, **kwargs)

        class Meta:
            abstract = True

    opts = {
        "fld_prefix": fld_prefix,
        f"{fld_prefix}": models.CharField(
            verbose_name=f"Has the patient started {verbose_name_label}?",
            max_length=15,
            choices=YES_NO_NA,
            default=YES,
        ),
        f"{fld_prefix}_date": models.DateField(
            verbose_name=f"Date started {verbose_name_label}",
            validators=[date_not_future],
            null=True,
            blank=True,
            help_text="If possible, provide the exact date here instead of estimating.",
        ),
        f"{fld_prefix}_ago": DurationYMDField(
            verbose_name=(
                f"If date not known, how long ago did the patient start {verbose_name_label}?"
            ),
            null=True,
            blank=True,
            help_text="If possible, provide the exact date above instead of estimating here.",
        ),
        f"{fld_prefix}_calculated_date": models.DateField(
            verbose_name=f"Estimated date started {verbose_name_label}",
            validators=[date_not_future],
            null=True,
            editable=False,
            help_text="Calculated based on response to `rx_init_ago`",
        ),
        f"{fld_prefix}_date_is_estimated": models.CharField(
            verbose_name=f"Was {verbose_name_label} start date estimated?",
            max_length=15,
            choices=YES_NO,
            default=NOT_APPLICABLE,
            editable=False,
        ),
    }

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel
