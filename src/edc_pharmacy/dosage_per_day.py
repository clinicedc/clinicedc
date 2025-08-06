from .constants import PER_DAY
from .dosage_calculator import DosageCalculator, DosageError


def dosage_per_day(dosage_guideline=None, **kwargs) -> float:
    if dosage_guideline.frequency_units.name != PER_DAY:
        raise DosageError(
            "Dosage is not calculated per day. Got dosage_guideline.frequency_units="
            f"{dosage_guideline.frequency_units.name}"
        )
    return DosageCalculator(dosage_guideline=dosage_guideline, **kwargs).dosage
