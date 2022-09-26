from __future__ import annotations

from edc_constants.constants import YES


class FastingFormValidatorMixin:
    def validate_fasting_required_fields(self, fasting_prefix: str | None = None):
        """Uses fields `fasting`,`fasting_duration_str`"""
        fasting_prefix = fasting_prefix or "fasting"
        self.required_if(
            YES, field=fasting_prefix, field_required=f"{fasting_prefix}_duration_str"
        )
