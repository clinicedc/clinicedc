from decimal import Decimal

from django import forms
from edc_reportable import MILLIMOLES_PER_LITER, convert_units


def validate_glucose_as_millimoles_per_liter(prefix, cleaned_data=None) -> None:
    min_val = Decimal("0.00")
    max_val = Decimal("30.00")
    high_value = Decimal("9999.99")
    value = cleaned_data.get(f"{prefix}_value")
    units = cleaned_data.get(f"{prefix}_units")
    if value and units:
        converted_value = convert_units(value, units_from=units, units_to=MILLIMOLES_PER_LITER)
        if (
            not (min_val <= round(converted_value, 2) <= max_val)
            and round(converted_value, 2) != high_value
        ):
            raise forms.ValidationError(
                {
                    f"{prefix}_value": (
                        f"This value is out-of-range. Got {converted_value} mmol/L"
                    )
                }
            )
