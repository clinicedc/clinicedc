from edc_constants.constants import FEMALE

from ...units import MICROMOLES_PER_LITER
from .base_egrfr import BaseEgfr


class EgfrCockcroftGault(BaseEgfr):

    """Reference https://www.mdcalc.com/creatinine-clearance-cockcroft-gault-equation

    Cockcroft-Gault

    eGFR (mL/min) = { (140 – age (years)) x weight (kg) x constant*} /
    serum creatinine (μmol/L)
    *constant = 1.23 for males and 1.05 for females

    Cockcroft-Gault CrCl, mL/min =
        (140 – age) × (weight, kg) × (0.85 if female) / (72 × SCr(mg/dL))

    """

    @property
    def value(self):
        if (
            self.gender
            and self.age_in_years
            and self.weight
            and self.scr.get(MICROMOLES_PER_LITER)
        ):
            return (self.age_factor * self.weight * self.gender_factor) / (
                self.scr.get(MICROMOLES_PER_LITER)
            )
        return None

    @property
    def gender_factor(self):
        return 1.05 if self.gender == FEMALE else 1.23
        # return 0.85 if self.gender == FEMALE else 1.00

    @property
    def age_factor(self):
        return 140 - self.age_in_years
