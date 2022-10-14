from __future__ import annotations

from decimal import Decimal

from edc_constants.constants import FEMALE
from edc_reportable import MICROMOLES_PER_LITER

from .base_egrfr import BaseEgfr, EgfrCalculatorError


class EgfrCockcroftGault(BaseEgfr):

    """Reference https://www.mdcalc.com/creatinine-clearance-cockcroft-gault-equation

    Cockcroft-Gault

    eGFR (mL/min) = { (140 – age (years)) x weight (kg) x constant*} /
    serum creatinine (μmol/L)
    *constant = 1.23 for males and 1.05 for females

    Cockcroft-Gault CrCl, mL/min =
        (140 – age) × (weight, kg) × (0.85 if female) / (72 × SCr(mg/dL))

    or:

    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2763564/

    GFR = 141 × min(Scr/κ, 1)α × max(Scr/κ, 1)-1.209 × 0.993Age
    """

    def __init__(self, weight: int | float | Decimal = None, **kwargs):
        self.weight = float(weight) if weight else None
        super().__init__(**kwargs)

    @property
    def value(self) -> float:
        """Returns the eGFR value or raises.

        eGFR (mL/min) = { (140 – age (years)) x weight (kg) x constant*} /
        serum creatinine (μmol/L)

        *constant = 1.23 for males and 1.05 for females
        """
        if (
            self.gender
            and self.age_in_years
            and self.weight
            and self.scr.get(MICROMOLES_PER_LITER)
        ):
            gender_factor = 1.05 if self.gender == FEMALE else 1.23
            adjusted_age = 140.00 - self.age_in_years
            value = (adjusted_age * self.weight * gender_factor) / float(
                self.scr.get(MICROMOLES_PER_LITER)
            )
            return value
        opts = dict(
            gender=self.gender,
            age_in_years=self.age_in_years,
            weight=self.weight,
            scr=self.scr.get(MICROMOLES_PER_LITER),
        )
        raise EgfrCalculatorError(
            f"Unable to calculate egfr_value. Insufficient information. Got {opts}."
        )
