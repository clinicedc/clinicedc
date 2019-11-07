from edc_constants.constants import MALE, FEMALE, OTHER, BLACK

from ..convert_units import convert_units
from ..units import MILLIGRAMS_PER_DECILITER
from .exceptions import CalculatorError


class eGFR:

    """Reference http://nephron.com/epi_equation

    Levey AS, Stevens LA, et al. A New Equation to Estimate Glomerular
    Filtration Rate. Ann Intern Med. 2009; 150:604-612.
    """

    def __init__(
        self,
        gender=None,
        age=None,
        ethnicity=None,
        creatinine=None,
        creatinine_units=None,
    ):
        """Expects creatinine (scr) in umols/L.

        Converts to creatinine to mg/dL for the calculation.
        """

        if not gender or gender not in [MALE, FEMALE]:
            raise CalculatorError(f"Invalid gender. Expected on of {MALE}, {FEMALE}")
        self.gender = gender

        if not (18 <= (age or 0) < 120):
            raise CalculatorError(
                f"Invalid age. See {self.__class__.__name__}. Got {age}"
            )
        self.age = float(age)

        self.ethnicity = ethnicity or OTHER
        self.scr = convert_units(
            creatinine, units_from=creatinine_units, units_to=MILLIGRAMS_PER_DECILITER
        )

    @property
    def value(self):
        return (
            141.000
            * (min(self.scr / self.kappa, 1.000) ** self.alpha)
            * (max(self.scr / self.kappa, 1.000) ** -1.209)
            * self.age_factor
            * self.gender_factor
            * self.ethnicity_factor
        )

    @property
    def alpha(self):
        return -0.329 if self.gender == FEMALE else -0.411

    @property
    def kappa(self):
        return 0.7 if self.gender == FEMALE else 0.9

    @property
    def ethnicity_factor(self):
        return 1.150 if self.ethnicity == BLACK else 1.000

    @property
    def gender_factor(self):
        return 1.018 if self.gender == FEMALE else 1.000

    @property
    def age_factor(self):
        return 0.993 ** self.age
