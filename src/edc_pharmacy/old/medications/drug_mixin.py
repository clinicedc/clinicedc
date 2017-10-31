

class DrugMixin:

    def __init__(self, body_weight=None, strength_of_vial=None,
                 millgrams_per_vial=None, duration=None):
        self.body_weight = body_weight
        self.strength_of_vial = strength_of_vial
        self.millgrams_per_vial = millgrams_per_vial
        self.duration = duration

    def round(self, value):
        new_value = int(round(value))
        return new_value if (
            new_value > value) else int(round(value)) + 1

    @property
    def required_quantity(self):
        return self.daily_dosage * self.duration

    @property
    def daily_dosage(self):
        """Returns dosage per day."""
        daily_dosage = ((self.millgrams_per_vial * self.body_weight) /
                        self.strength_of_vial)
        return round(daily_dosage)
