from .drug_mixin import DrugMixin


class VialDosage(DrugMixin):
    """
    Calculates drug dosage for vials.
    """

    def __init__(
        self,
        body_weight=None,
        strength_of_vial=None,
        millgrams_per_vial=None,
        duration=None,
        use_body_weight=None,
    ):
        self.body_weight = body_weight
        self.strength_of_vial = strength_of_vial
        self.millgrams_per_vial = millgrams_per_vial
        self.duration = duration
        self.use_body_weight = use_body_weight

    @property
    def daily_dosage(self):
        """Returns dosage per day."""
        try:
            daily_dosage = float(self.millgrams_per_vial) * float(self.body_weight)
            daily_dosage = daily_dosage / float(self.strength_of_vial)
        except TypeError as e:
            raise Exception(
                f"{self.millgrams_per_vial} * {self.body_weight} "
                f"/ {self.strength_of_vial} Got {e}"
            )
        return round(daily_dosage)

    @property
    def __repr__(self):
        return f"{self.definition.description}"
