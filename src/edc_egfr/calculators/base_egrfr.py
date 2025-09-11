from __future__ import annotations

from edc_constants.constants import FEMALE, MALE
from edc_reportable import MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER
from edc_reportable.utils import convert_units


class EgfrCalculatorError(Exception):
    pass


class BaseEgfr:
    def __init__(
        self,
        gender: str | None = None,
        age_in_years: int | float | None = None,
        creatinine_value: float | int | None = None,
        creatinine_units: str | None = None,
        **kwargs,  # noqa
    ):
        """Expects creatinine (scr) in umols/L.

        Converts to creatinine to mg/dL for the calculation.
        """
        self.scr = {}
        if not gender or gender not in [MALE, FEMALE]:
            raise EgfrCalculatorError(
                f"Invalid gender. Expected one of {MALE}, {FEMALE}. Got {gender}."
            )
        self.gender = gender
        if not (18 <= (age_in_years or 0) < 120):
            raise EgfrCalculatorError(
                f"Invalid age. See {self.__class__.__name__}. Got {age_in_years}"
            )
        self.age_in_years = float(age_in_years) if age_in_years else None
        if creatinine_value and creatinine_units:
            self.scr.update(
                {
                    MILLIGRAMS_PER_DECILITER: convert_units(
                        label="creatinine",
                        value=float(creatinine_value),
                        units_from=creatinine_units,
                        units_to=MILLIGRAMS_PER_DECILITER,
                    )
                }
            )
            self.scr.update(
                {
                    MICROMOLES_PER_LITER: convert_units(
                        label="creatinine",
                        value=float(creatinine_value),
                        units_from=creatinine_units,
                        units_to=MICROMOLES_PER_LITER,
                    )
                }
            )
