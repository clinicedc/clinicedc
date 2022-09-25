from datetime import date
from typing import Any, Optional

from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import YES
from edc_dx import Diagnoses
from edc_dx.utils import calculate_dx_date_if_estimated
from edc_model import models as edc_models
from edc_model.validators import date_not_future


class InitialReviewModelError(Exception):
    pass


def initial_dx_model_mixin_factory(dx_field_prefix: Optional[str] = None):
    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    dx_field_prefix = f"{dx_field_prefix}_" if dx_field_prefix else ""

    opts = {
        f"{dx_field_prefix}dx_ago": edc_models.DurationYMDField(
            verbose_name="How long ago was the patient diagnosed?",
            null=True,
            blank=True,
            help_text="If possible, provide the exact date below instead of estimating here.",
        ),
        f"{dx_field_prefix}dx_date": models.DateField(
            verbose_name="Date patient diagnosed",
            null=True,
            blank=True,
            validators=[date_not_future],
            help_text="If possible, provide the exact date here instead of estimating above.",
        ),
        f"{dx_field_prefix}dx_estimated_date": models.DateField(
            verbose_name="Estimated diagnoses date",
            null=True,
            help_text=f"Calculated based on response to `{dx_field_prefix}dx_ago`",
            editable=False,
        ),
        f"{dx_field_prefix}dx_date_is_estimated": models.CharField(
            verbose_name="Was the diagnosis date estimated?",
            max_length=15,
            choices=YES_NO,
            default=YES,
            editable=False,
        ),
    }

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel


class InitialReviewMethodsModelMixin(models.Model):
    def save(self: Any, *args, **kwargs):
        diagnoses = Diagnoses(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            lte=True,
        )
        if not diagnoses.get_dx_by_model(self) == YES:
            raise InitialReviewModelError(
                "No diagnosis has been recorded. See clinical review. "
                "Perhaps catch this in the form."
            )
        self.dx_estimated_date, self.dx_date_is_estimated = calculate_dx_date_if_estimated(
            self.dx_date,
            self.dx_ago,
            self.report_datetime,
        )
        super().save(*args, **kwargs)

    def get_best_dx_date(self: Any) -> date:
        return self.dx_date or self.dx_estimated_date

    class Meta:
        abstract = True
        # TODO: add constraint on diagnosis, this is a singlton


class InitialReviewModelMixin(
    initial_dx_model_mixin_factory(), InitialReviewMethodsModelMixin, models.Model
):
    class Meta:
        abstract = True
        # TODO: add constraint on diagnosis, this is a singlton
