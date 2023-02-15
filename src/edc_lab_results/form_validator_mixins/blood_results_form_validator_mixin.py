from collections import namedtuple
from typing import Any

from edc_constants.constants import NO, YES
from edc_lab.form_validators import CrfRequisitionFormValidatorMixin
from edc_reportable import ReportablesFormValidatorMixin


class BloodResultsFormValidatorError(Exception):
    pass


class BloodResultsFormValidatorMixin(
    ReportablesFormValidatorMixin,
    CrfRequisitionFormValidatorMixin,
):
    value_field_suffix = "_value"
    panel = None
    panels = None
    is_poc_field = "is_poc"

    def evaluate_value(self, field_name):
        """A hook to evaluate a field value"""
        pass

    def clean(self: Any) -> None:
        # do not require requisition if poc
        self.required_if(NO, field=self.is_poc_field, field_required="requisition")
        self.required_if_true(
            not self.is_poc and any(self.fields_names_with_values),
            field_required=self.requisition_field,
        )

        if self.requisition:
            for fields_name in self.fields_names_with_values:
                try:
                    utest_id, _ = fields_name.split(self.value_field_suffix)
                except ValueError:
                    utest_id = fields_name
                if f"{utest_id}_units" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_units",
                        field_required_evaluate_as_int=True,
                    )
                if f"{utest_id}_abnormal" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_abnormal",
                        field_required_evaluate_as_int=True,
                    )
                if f"{utest_id}_reportable" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_reportable",
                        field_required_evaluate_as_int=True,
                    )
                self.evaluate_value(f"{utest_id}_value")
            self.validate_reportable_fields(
                self.requisition.panel_object.reference_range_collection_name,
                **self.reportables_evaluator_options,
            )

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
        if self.cleaned_data.get(self.is_poc_field):
            return self.cleaned_data.get(self.is_poc_field) == YES
        return False

    @property
    def fields_names_with_values(self: Any) -> list:
        """Returns a list result `value` fields that are not None"""
        fields_names_with_values = []
        field_names = [f"{utest_id}{self.value_field_suffix}" for utest_id in self.utest_ids]
        for field_name in field_names:
            if self.cleaned_data.get(field_name):
                fields_names_with_values.append(field_name)
        return field_names

    @property
    def utest_ids(self: Any) -> list:
        utest_ids = []
        for panel in self.panel_list:
            for utest_id in panel.utest_ids:
                try:
                    utest_id, _ = utest_id
                except ValueError:
                    pass
                utest_ids.append(utest_id)
        return utest_ids

    @property
    def panel_list(self: Any) -> list:
        if self.panel:
            return [self.panel]
        return self.panels
