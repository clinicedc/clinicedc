from typing import Optional

from edc_constants.constants import BLACK, FEMALE

# TODO: https://www.rcpa.edu.au/Manuals/RCPA-Manual/
#  Pathology-Tests/C/Creatinine-clearance-Cockcroft-and-Gault
from ...units import MILLIGRAMS_PER_DECILITER
from .base_egrfr import BaseEgfr


class EgfrCkdEpi(BaseEgfr):  # noqa

    """Reference https://nephron.com/epi_equation

    CKD-EPI Creatinine equation

    Levey AS, Stevens LA, et al. A New Equation to Estimate Glomerular
    Filtration Rate. Ann Intern Med. 2009; 150:604-612.
    """

    @property
    def value(self) -> Optional[float]:
        if (
            self.gender
            and self.age_in_years
            and self.ethnicity
            and self.scr.get(MILLIGRAMS_PER_DECILITER)
        ):
            scr = self.scr.get(MILLIGRAMS_PER_DECILITER)
            return (
                141.000
                * (min(scr / self.kappa, 1.000) ** self.alpha)
                * (max(scr / self.kappa, 1.000) ** -1.209)
                * self.age_factor
                * self.gender_factor
                * self.ethnicity_factor
            )
        return None

    @property
    def alpha(self) -> float:
        return -0.329 if self.gender == FEMALE else -0.411

    @property
    def kappa(self) -> float:
        return 0.7 if self.gender == FEMALE else 0.9

    @property
    def ethnicity_factor(self) -> float:
        return 1.150 if self.ethnicity == BLACK else 1.000

    @property
    def gender_factor(self) -> float:
        return 1.018 if self.gender == FEMALE else 1.000

    @property
    def age_factor(self) -> float:
        return 0.993**self.age_in_years
