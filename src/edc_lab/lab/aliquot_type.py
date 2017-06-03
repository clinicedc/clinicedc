
class AliquotType:

    """A class to represent an aliquot type by an alpha and
    numeric code.

    An aliquot type manages a list of valid derivatives.
    """

    def __init__(self, name=None, alpha_code=None, numeric_code=None):
        self.derivatives = []
        self.name = name
        self.alpha_code = alpha_code
        self.numeric_code = numeric_code

    def __repr__(self):
        return '{self.__class__.__name__}({self.name}, {self.alpha_code}, {self.numeric_code})'

    def __str__(self):
        alpha_code = self.alpha_code or '?alpha_code'
        numeric_code = self.numeric_code or '?numeric_code'
        return f'{self.name.title()} ({alpha_code}:{numeric_code})'

    def add_derivatives(self, *aliquot_type):
        self.derivatives.extend(aliquot_type)
