import contextlib
from collections import namedtuple
from typing import Any

from edc_constants.constants import NO, NULL_STRING, YES
from edc_lab import RequisitionPanel
from edc_lab.form_validators import CrfRequisitionFormValidatorMixin
from edc_reportable.forms import ReportablesFormValidatorMixin


class BloodResultsFormValidatorError(Exception):
    pass


class BloodResultsFormValidatorMixin(
    ReportablesFormValidatorMixin,
    CrfRequisitionFormValidatorMixin,
):
    value_field_suffix = "_value"
    panel: RequisitionPanel = None
    panels: tuple[RequisitionPanel, ...] = ()
    is_poc_field: str = "is_poc"

    def evaluate_value(self, **kwargs):
        """A hook to evaluate a field value"""
        pass

    def clean(self: Any) -> None:
        if self.cleaned_data.get(self.is_poc_field) not in [None, NULL_STRING]:
            # do not require requisition if poc == YES
            self.required_if(NO, field=self.is_poc_field, field_required="requisition")
        else:
            # requires requisition if any `value` fields have value but inverse not True.
            # It is OK to submit the requisition without any `value` fields data.
            self.required_if_true(
                any(self.fields_names_with_values),
                field_required=self.requisition_field,
                inverse=False,
            )

        if self.requisition:
            for fields_name in self.fields_names_with_values:
                try:
                    utest_id, _ = fields_name.split(self.value_field_suffix)
                except ValueError:
                    utest_id = fields_name
                if f"{utest_id}_units" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or NULL_STRING}",
                        field_required=f"{utest_id}_units",
                        field_required_evaluate_as_int=True,
                    )
                if f"{utest_id}_abnormal" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or NULL_STRING}",
                        field_required=f"{utest_id}_abnormal",
                        field_required_evaluate_as_int=False,
                    )
                if f"{utest_id}_reportable" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or NULL_STRING}",
                        field_required=f"{utest_id}_reportable",
                        field_required_evaluate_as_int=False,
                    )
                self.evaluate_value(prefix=utest_id)
            self.validate_reportable_fields(
                self.requisition.panel_object.reference_range_collection_name,
                **self.reportables_evaluator_options,
            )
        super().clean()

    @property
    def requisition(self: Any):
        """Returns a Requisition instance or raises
        forms ValidationError.

        If POC, Requisition instance is not a model
        """
        if self.cleaned_data.get(self.is_poc_field) == YES:
            Requisition = namedtuple("Requisition", "panel_object")
            return Requisition(self.panel)
        return self.validate_requisition(*self.panel_list)

    @property
    def is_poc(self: Any) -> bool:
        if self.is_poc_field and self.cleaned_data.get(self.is_poc_field):
            return self.cleaned_data.get(self.is_poc_field) == YES
        return False

    @property
    def fields_names_with_values(self: Any) -> tuple[str, ...]:
        """Returns a list result `value` field names that are not None."""
        field_names = (f"{utest_id}{self.value_field_suffix}" for utest_id in self.utest_ids)
        return tuple(
            [
                field_name
                for field_name in field_names
                if self.cleaned_data.get(field_name) not in [None, NULL_STRING]
            ]
        )

    @property
    def utest_ids(self: Any) -> tuple:
        utest_ids = []
        for panel in self.panel_list:
            for utest_id in panel.utest_ids:
                with contextlib.suppress(ValueError):
                    utest_id, _ = utest_id
                utest_ids.append(utest_id)
        return tuple(utest_ids)

    @property
    def panel_list(self: Any) -> tuple[RequisitionPanel]:
        if self.panel:
            return (self.panel,)
        return self.panels
