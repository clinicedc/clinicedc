from dateutil.relativedelta import relativedelta
from edc_utils import age, get_utcnow
from edc_utils.round_up import round_half_away_from_zero

from .exceptions import CalculatorError


class BMI:
    """Calculate BMI, raise if not adult."""

    def __init__(
        self,
        weight_kg=None,
        height_cm=None,
        lower_bmi_value=None,
        upper_bmi_value=None,
        dob=None,
        report_datetime=None,
        **kwargs,
    ):
        if not weight_kg or not height_cm:
            raise CalculatorError(f"Unable to calculate BMI. Got {weight_kg}kg, {height_cm}cm")
        if age(dob, report_datetime).years < 18:
            raise CalculatorError("Unable to calculate BMI. Got age<18")
        self.lower = float(lower_bmi_value or 5.0)
        self.upper = float(upper_bmi_value or 75.0)
        self.weight = float(weight_kg)
        self.height = float(height_cm) / 100.0
        self.raw_bmi_value = self.weight / (self.height**2)
        if not (self.lower <= self.raw_bmi_value <= self.upper):
            raise CalculatorError(
                "BMI value is absurd. "
                f"Using {self.weight}kg, {self.height}m. Got {self.value}."
            )

    @property
    def value(self):
        return round_half_away_from_zero(self.raw_bmi_value, 4)


def calculate_bmi(
    weight_kg=None,
    height_cm=None,
    lower_bmi_value=None,
    upper_bmi_value=None,
    dob=None,
    report_datetime=None,
    **kwargs,
):
    """Returns a BMI instance or None.

    Assumes adult dob (18) if dob not provided."""
    bmi = None
    if height_cm and weight_kg:
        report_datetime = report_datetime or get_utcnow()
        bmi = BMI(
            weight_kg=weight_kg,
            height_cm=height_cm,
            lower_bmi_value=lower_bmi_value,
            upper_bmi_value=upper_bmi_value,
            dob=dob or report_datetime - relativedelta(years=18),
            report_datetime=report_datetime,
            **kwargs,
        )
    return bmi
