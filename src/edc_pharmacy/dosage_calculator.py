from decimal import Decimal
from typing import Any, Optional, Union


class DosageError(Exception):
    pass


class DosageCalculator:
    def __init__(
        self,
        dosage_guideline: Optional[Any] = None,
        formulation: Optional[Any] = None,
        weight_in_kgs: Optional[Union[float, Decimal]] = None,
    ) -> None:
        self.dosage_guideline = dosage_guideline
        self.formulation = formulation
        if formulation.medication != dosage_guideline.medication:
            raise DosageError(
                "Medication mismatch. Guideline medication does not match formulation. "
                f"Got guideline.{dosage_guideline.medication} != formulation."
                f"{formulation.medication}."
            )
        if formulation.units.name != dosage_guideline.dose_units.name:
            raise DosageError(
                f"Invalid units. Guideline dose is in "
                f"'{dosage_guideline.dose_units}'. Got {formulation.units.name}."
            )
        if dosage_guideline.dose_per_kg and not weight_in_kgs:
            raise DosageError(
                "Expected weight_in_kgs for dosage_guideline dose in kgs. Got None"
            )
        self.weight_in_kgs = weight_in_kgs

    @property
    def dosage(self) -> float:
        """Returns the dosage as a float.

        The dosage is the dose in the units of dispensing, e.g 5, which
        might be expressed as 5 tabs 3 x per day

        The formulation_type and frequency of the dose depends on the formulation
        and dosage guideline.
        """
        return float(self.dose / float(self.strength))

    @property
    def strength(self):
        return self.formulation.strength

    @property
    def strength_units(self):
        return self.formulation.units.name

    @property
    def frequency(self):
        return self.dosage_guideline.frequency

    @property
    def dose_per_kg(self):
        return self.dosage_guideline.dose_per_kg

    @property
    def dose(self) -> float:
        """Returns the dose to be administered per day/hr or
        whatever the freq is.

        This is the guideline dose unless weight is factored in.

        """
        if self.weight_in_kgs and self.dose_per_kg:
            return float(self.dose_per_kg) * float(self.weight_in_kgs)
        return float(self.dosage_guideline.dose)
