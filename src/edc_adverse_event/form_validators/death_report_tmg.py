from __future__ import annotations

from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED, NO, OTHER
from edc_form_validators import INVALID_ERROR, FormValidator

from ..form_validator_mixins import (
    BaseRequiresDeathReportFormValidatorMixin,
    DeathReportFormValidatorMixin,
)
from ..utils import get_ae_model


class DeathReportTmgFormValidator(
    DeathReportFormValidatorMixin, BaseRequiresDeathReportFormValidatorMixin, FormValidator
):
    @property
    def death_date(self) -> date:
        try:
            obj = get_ae_model("deathreport").objects.get(
                subject_identifier=self.cleaned_data.get("subject_identifier")
            )
        except ObjectDoesNotExist:
            self.raise_validation_error("Death report not found.", INVALID_ERROR)
        death_date = getattr(obj, getattr(obj, "death_date_field"))
        try:
            death_date = death_date.date()
        except AttributeError:
            pass
        return death_date

    def clean(self):
        self.date_is_after_or_raise(
            field="report_datetime",
            reference_value=self.death_report_date,
            inclusive=True,
        )

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death",
            inverse=False,
        )

        self.validate_other_specify(
            field="cause_of_death",
            other_specify_field="cause_of_death_other",
            other_stored_value=OTHER,
        )

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death_agreed",
            inverse=False,
        )

        self.required_if(
            NO, field="cause_of_death_agreed", field_required="narrative", inverse=False
        )

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )

        if self.cleaned_data.get("report_closed_datetime"):
            self.date_is_after_or_raise(
                field="report_closed_datetime",
                reference_field="report_datetime",
                inclusive=True,
                msg="Must be on or after the report date above.",
            )
