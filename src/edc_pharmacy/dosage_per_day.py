from decimal import Decimal
from typing import Optional, Union


class DosageError(Exception):
    pass


def dosage_per_day(
    dosage_guideline,
    strength: Optional[Union[float, Decimal]] = None,
    strength_units: Optional[str] = None,
    weight_in_kgs: Optional[Union[float, Decimal]] = None,
):
    strength = strength or 1.0
    weight_in_kgs = weight_in_kgs or 1.0
    if strength_units != dosage_guideline.dose_units.name:
        raise DosageError(
            f"Invalid units. Guideline dose is in "
            f"'{dosage_guideline.dose_units}'. Got {strength_units}."
        )
    return (
        float(dosage_guideline.dose or dosage_guideline.dose_per_kg)
        * float(weight_in_kgs)
        * float(dosage_guideline.frequency)
    ) / float(strength)
