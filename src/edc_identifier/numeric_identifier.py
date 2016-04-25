from .checkdigit_mixins import ModulusMixin
from .exceptions import IdentifierError
from .identifier_with_checkdigit import IdentifierWithCheckdigit


class NumericIdentifier(IdentifierWithCheckdigit):
    """Class for numeric identifier with check digit."""

    name = 'numericidentifier'
    identifier_pattern = r'^[0-9]{10}$'
    checkdigit_pattern = r'^[0-9]{1}$'
    separator = None
    seed = ('0000000000')

    def increment(self, identifier):
        """Returns the incremented identifier."""
        if int(identifier) < self.max_numeric(identifier):
            incr = int(identifier) + 1
        elif int(identifier) == self.max_numeric(identifier):
            incr = 1
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))
        frmt = '{{0:0{}d}}'.format(len(identifier))
        identifier = '{}'.format(frmt.format(incr))
        return identifier

    def max_numeric(self, identifier):
        """Returns max value for numeric segment."""
        return int('9' * len(identifier))


class NumericIdentifierWithModulus(ModulusMixin, NumericIdentifier):
    modulus = 13
