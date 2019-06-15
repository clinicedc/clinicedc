class ScreeningEligibility:
    def __init__(self, model_obj=None, allow_none=None, *kwargs):
        self.model_obj = model_obj
        self.allow_none = allow_none

    @property
    def eligible(self):
        """Returns True or False.
        """
        return False

    @property
    def reasons_ineligible(self):
        """Returns a dictionary of reasons ineligible.
        """
        return {}
