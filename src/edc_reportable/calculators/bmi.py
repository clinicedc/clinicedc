from .exceptions import CalculatorError


class BMI:
    """Calculate BMI, assume adult.
    """

    def __init__(self, weight_kg=None, height_cm=None):
        if not weight_kg or not height_cm:
            raise CalculatorError(
                f"Unable to calculate BMI. Got {weight_kg}kg, {height_cm}cm"
            )
        self.lower, self.upper = 5.0, 60.0
        self.weight = float(weight_kg)
        self.height = float(height_cm) / 100.0
        self.bmi = self.weight / (self.height ** 2)

    @property
    def value(self):
        if not (self.lower <= self.bmi <= self.upper):
            raise CalculatorError(
                f"BMI value is absurd. Using {self.weight}kg, {self.height}m. Got {self.bmi}."
            )
        return self.bmi
