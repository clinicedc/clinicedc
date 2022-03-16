from typing import Optional

from edc_constants.constants import YES


class FbgFormValidatorMixin:
    def validate_fbg_required_fields(self, fbg_prefix: Optional[str] = None):
        """Uses fields `fbg_value`, `fbg_datetime`, `fbg_units`"""
        fbg_prefix = fbg_prefix or "fbg"

        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_datetime"),
            field_required=f"{fbg_prefix}_value",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_value"),
            field_required=f"{fbg_prefix}_units",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_value"),
            field_required=f"{fbg_prefix}_datetime",
        )
