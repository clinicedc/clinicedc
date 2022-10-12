from edc_constants.constants import YES

from edc_screening.fc import FC
from edc_screening.screening_eligibility import ScreeningEligibility


class MyScreeningEligibility(ScreeningEligibility):
    def __init__(self, **kwargs):
        self.age_in_years = None
        self.alive = None
        super().__init__(**kwargs)

    def get_required_fields(self):
        return {
            "age_in_years": FC(lambda x: x >= 18, "must be >=18"),
            "alive": FC(YES, "must be alive"),
        }
