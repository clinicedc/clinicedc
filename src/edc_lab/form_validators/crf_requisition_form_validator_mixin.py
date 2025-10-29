from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from edc_utils.date import to_local
from edc_utils.text import formatted_datetime

if TYPE_CHECKING:
    from ..model_mixins import RequisitionModelMixin


class CrfRequisitionFormValidatorMixin:
    """An FormValidator mixin for CRFs (not requisitions).

    Used with a CRF that refers to a requisition or requisitions.

    Call in FormValidator.clean.

    For test 'xxx' expects the field trio of 'requisition' and
    'assay_datetime', 'xxx_panel'

        self.required_if_true(
            self.cleaned_data.get('cd4') is not None,
            field_required='cd4_requisition')
        self.validate_requisition(
            'cd4_requisition', 'cd4_assay_datetime', cd4_panel)

    See also, for example: ambition_form_validators.form_validators.blood_result
    """

    assay_datetime_field: str = "assay_datetime"
    requisition_field: str = "requisition"
    allow_assay_datetime_after_report_datetime = True

    def validate_requisition(
        self,
        *panels,
        requisition_field: str | None = None,
        assay_datetime_field: str | None = None,
    ) -> RequisitionModelMixin:
        """Validates that the requisition model instance exists
        and assay datetime provided.
        """
        requisition_field = requisition_field or self.requisition_field
        requisition = self.cleaned_data.get(requisition_field)
        assay_datetime_field = assay_datetime_field or self.assay_datetime_field
        if requisition and requisition.panel_object not in panels:
            raise forms.ValidationError(
                {
                    requisition_field: (
                        "Incorrect requisition. Unknown panel. "
                        f"Expected one of {[p.name for p in panels]}. "
                        f"Got {requisition.panel_object.name}"
                    )
                }
            )

        self.required_if_true(requisition, field_required=assay_datetime_field)

        self.validate_assay_datetime(requisition, assay_datetime_field)
        return requisition

    def validate_assay_datetime(
        self,
        requisition: RequisitionModelMixin,
        assay_datetime_field: str | None = None,
    ) -> None:
        """Validate assay datetime is on or after requisition
        datetime.

        If `allow_assay_datetime_after_report_datetime` is False,
        raise if assay datetime is after report_datetime.

        """
        assay_datetime = self.cleaned_data.get(
            assay_datetime_field or self.assay_datetime_field
        )
        if (
            not self.allow_assay_datetime_after_report_datetime
            and assay_datetime
            and assay_datetime > self.report_datetime
        ):
            raise forms.ValidationError(
                {assay_datetime_field: "Invalid. Cannot be after report datetime."}
            )
        if assay_datetime and assay_datetime < requisition.requisition_datetime:
            raise forms.ValidationError(
                {
                    assay_datetime_field: (
                        "Invalid. Cannot be before requisition date. Requisition date is "
                        f"{formatted_datetime(to_local(requisition.requisition_datetime))}."
                    )
                }
            )
