from __future__ import annotations

from datetime import date

from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE, YES
from edc_dx import Diagnoses
from edc_model.models import DurationYMDField
from edc_model.utils import get_report_datetime_field_name
from edc_model.validators import date_not_future

from .calculate_date import update_calculated_date


class InitialReviewModelError(Exception):
    pass


def dx_initial_review_methods_model_mixin_factory():
    class AbstractModel(models.Model):
        fld_prefix: str | None = None

        def save(self, *args, **kwargs):
            if not self.diagnoses.get_dx_by_model(self) == YES:
                raise InitialReviewModelError(
                    "No diagnosis has been recorded. See clinical review. "
                    "Perhaps catch this in the form."
                )
            update_calculated_date(
                self,
                fld_prefix=self.fld_prefix,
                reference_field=get_report_datetime_field_name(),
            )
            super().save(*args, **kwargs)

        @property
        def diagnoses(self):
            subject_identifier = getattr(self, "subject_identifier")
            return Diagnoses(
                subject_identifier=subject_identifier,
                report_datetime=getattr(self, get_report_datetime_field_name()),
                lte=True,
            )

        def get_best_dx_date(self) -> date:
            return getattr(self, f"{self.fld_prefix}_date") or getattr(
                self, f"{self.fld_prefix}_calculated_date"
            )

        class Meta:
            abstract = True

    return AbstractModel


def dx_initial_review_model_mixin_factory(fld_prefix: str | None = None):
    fld_prefix = fld_prefix or "dx"

    class AbstractModel(dx_initial_review_methods_model_mixin_factory(), models.Model):
        class Meta:
            abstract = True

    opts = {
        "fld_prefix": fld_prefix,
        f"{fld_prefix}_date": models.DateField(
            verbose_name="Date patient diagnosed",
            null=True,
            blank=True,
            validators=[date_not_future],
            help_text="If possible, provide the exact date here instead of estimating.",
        ),
        f"{fld_prefix}_ago": DurationYMDField(
            verbose_name="If date not known, how long ago was the patient diagnosed?",
            null=True,
            blank=True,
            help_text="If possible, provide the exact date above instead of estimating here.",
        ),
        f"{fld_prefix}_calculated_date": models.DateField(
            verbose_name="Estimated diagnosis date",
            null=True,
            help_text=f"Calculated based on response to `{fld_prefix}dx_ago`",
            editable=False,
        ),
        f"{fld_prefix}_date_is_estimated": models.CharField(
            verbose_name="Was the diagnosis date estimated?",
            max_length=15,
            choices=YES_NO,
            default=NOT_APPLICABLE,
            editable=False,
        ),
    }

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel
