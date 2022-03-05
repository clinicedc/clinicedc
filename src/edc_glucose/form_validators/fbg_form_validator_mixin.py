from typing import Optional

from edc_constants.constants import YES


class FbgFormValidatorMixin:
    def validate_fbg_required_fields(self, prefix: Optional[str] = None):
        """Uses fields `fasting`,`fasting_duration_str`, `ifg_value`,
        `ifg_datetime`, `ifg_units`
        """
        prefix = "ifg" or prefix
        self.required_if(YES, field="fasting", field_required="fasting_duration_str")

        self.required_if(YES, field="fasting", field_required=f"{prefix}_datetime")

        self.required_if(YES, field="fasting", field_required=f"{prefix}_value")

        self.required_if_true(
            self.cleaned_data.get(f"{prefix}_datetime"),
            field_required=f"{prefix}_value",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{prefix}_value"),
            field_required=f"{prefix}_units",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{prefix}_value"),
            field_required=f"{prefix}_datetime",
        )
