from edc_constants.constants import MALE, FEMALE


class GenderEvaluator:
    def __init__(self, gender=None, **kwargs):
        self.eligible = False
        self.reasons_ineligible = None
        if gender == MALE:
            self.eligible = True
        elif gender == FEMALE:
            self.eligible = True
        if not self.eligible:
            self.reasons_ineligible = []
            if gender not in [MALE, FEMALE]:
                self.reasons_ineligible.append(f"{gender} is an invalid gender.")
