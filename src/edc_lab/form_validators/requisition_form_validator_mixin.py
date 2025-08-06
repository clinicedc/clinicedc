from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps
from edc_constants.constants import NO, YES
from edc_utils import to_utc

if TYPE_CHECKING:
    from ..models import Aliquot


class RequisitionFormValidatorError(Exception):
    pass


class RequisitionFormValidatorMixin:
    aliquot_model: str = "edc_lab.aliquot"

    def clean(self) -> None:
        if self.instance:
            if self.cleaned_data.get("packed") != self.instance.packed:
                raise forms.ValidationError({"packed": "Value may not be changed here."})
            elif self.cleaned_data.get("processed") != self.instance.processed:
                if self.aliqout_model_cls.objects.filter(
                    requisition_identifier=self.instance.requisition_identifier
                ).exists():
                    raise forms.ValidationError(
                        {"processed": "Value may not be changed. Aliquots exist."}
                    )
            elif not self.cleaned_data.get("received") and self.instance.received:
                if self.instance.processed:
                    raise forms.ValidationError(
                        {"received": "Specimen has already been processed."}
                    )
            elif self.cleaned_data.get("received") and not self.instance.received:
                raise forms.ValidationError(
                    {"received": "Receive specimens in the lab section of the EDC."}
                )
            elif self.instance.received:
                raise forms.ValidationError(
                    "Requisition may not be changed. The specimen has "
                    "already been received."
                )

        self.applicable_if(NO, field="is_drawn", field_applicable="reason_not_drawn")
        self.validate_other_specify(field="reason_not_drawn")
        self.required_if(YES, field="is_drawn", field_required="drawn_datetime")
        self.validate_drawn_datetime()
        self.applicable_if(YES, field="is_drawn", field_applicable="item_type")
        self.required_if(YES, field="is_drawn", field_required="item_count")
        self.required_if(YES, field="is_drawn", field_required="estimated_volume")

    @property
    def aliqout_model_cls(self) -> Aliquot:
        return django_apps.get_model(self.aliquot_model)

    @property
    def requisition_datetime(self) -> datetime | None:
        """Returns the requisition_datetime.

        `report_datetime` exists on the model but is always
        the same as `requisition_datetime`. See model.save().

        Note value of attr `report_datetime_field_attr`.
        """
        if self.report_datetime_field_attr != "requisition_datetime":
            raise RequisitionFormValidatorError(
                "Invalid value `report_datetime_field_attr`. Expected `requisition_datetime`. "
                f"Got `{self.report_datetime_field_attr}`."
            )
        return self.report_datetime

    def validate_drawn_datetime(self) -> None:
        if (
            self.requisition_datetime
            and self.cleaned_data.get("drawn_datetime")
            and to_utc(self.cleaned_data.get("drawn_datetime")).date()
            > to_utc(self.requisition_datetime).date()
        ):
            raise forms.ValidationError(
                {"drawn_datetime": "Invalid. Cannot be after requisition date."}
            )
