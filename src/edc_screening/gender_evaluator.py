from edc_constants.constants import FEMALE, MALE


class GenderEvaluator:
    eligible_gender = [MALE, FEMALE]

    def __init__(self, gender=None, **kwargs) -> None:  # noqa
        self.eligible = False
        self.reasons_ineligible = None
        if gender in self.eligible_gender:
            self.eligible = True
        else:
            self.reasons_ineligible = f"`{gender}` is an invalid."
