INVALID_SCREENING_IDENTIFIER = "INVALID_SCREENING_IDENTIFIER"


class ScreeningEligibilityError(Exception):
    pass


class ScreeningEligibilityAttributeError(Exception):
    pass


class ScreeningEligibilityModelAttributeError(Exception):
    pass


class ScreeningEligibilityCleanedDataKeyError(Exception):
    pass


class ScreeningEligibilityInvalidCombination(Exception):
    pass


class RequiredFieldValueMissing(Exception):
    pass


class InvalidScreeningIdentifierFormat(Exception):
    def __init__(self, *args, **kwargs):
        self.code = INVALID_SCREENING_IDENTIFIER
        super().__init__(*args, **kwargs)
