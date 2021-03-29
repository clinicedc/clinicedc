import re


class AliquotTypeAlphaCodeError(Exception):
    pass


class AliquotTypeNumericCodeError(Exception):
    pass


class AliquotType:

    """A class to represent an aliquot type by an alpha and
    numeric code.

    An aliquot type manages a list of valid derivatives for the
    aliquot type, e.g. WB->Plasma, WB->Buffy Coat.
    """

    def __init__(self, name: str = None, alpha_code: str = None, numeric_code: str = None):
        self.derivatives = []
        self.name = name
        if not alpha_code or not re.match(r"^[A-Z]+$", alpha_code, re.ASCII):
            raise AliquotTypeAlphaCodeError(f"Invalid alpha code. Got {alpha_code}.")
        else:
            self.alpha_code = alpha_code
        if not numeric_code or not re.match(r"^\d+$", numeric_code, re.ASCII):
            raise AliquotTypeNumericCodeError(f"Invalid numeric code. Got {numeric_code}.")
        else:
            self.numeric_code = numeric_code

    def __repr__(self):
        return "{self.__class__.__name__}({self.name}, {self.alpha_code}, {self.numeric_code})"

    def __str__(self):
        alpha_code = self.alpha_code or "?alpha_code"
        numeric_code = self.numeric_code or "?numeric_code"
        return f"{self.name.title()} ({alpha_code}:{numeric_code})"

    def add_derivatives(self, *aliquot_type: "AliquotType") -> None:
        """Adds an aliquot instance that is a valid
        derivative of self.
        """
        self.derivatives.extend(aliquot_type)
