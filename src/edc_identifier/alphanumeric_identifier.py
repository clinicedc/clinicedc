import re

from .checkdigit_mixins import LuhnOrdMixin
from .exceptions import IdentifierError
from .numeric_identifier import NumericIdentifier


class AlphanumericIdentifier(LuhnOrdMixin, NumericIdentifier):

    name = 'alphanumericidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']
    separator = None

    def __init__(self, last_identifier=None, prefix=None):
        self.identifier_pattern = '{}{}'.format(self.alpha_pattern[:-1], self.numeric_pattern[1:])
        self.verify_seed()
        super(AlphanumericIdentifier, self).__init__(last_identifier, prefix=prefix)

    def verify_seed(self):
        """Verifies the class attribute "seed" matches the regular expressions
        of alpha and numeric and adds a checkdigit to the numeric segment."""
        if not isinstance(self.seed, list):
            raise TypeError('Expected attribute seed to be a list. Got {}'.format(self.seed))
        re.match(self.alpha_pattern, self.seed[0]).group()
        re.match(self.numeric_pattern, self.seed[1]).group()

    @property
    def identifier_pattern_with_checkdigit(self):
        return '{}{}'.format(self.identifier_pattern[:-1], self.checkdigit_pattern[1:])

    def increment(self, identifier):
        """Returns the incremented identifier."""
        identifier = '{}{}{}'.format(
            self.prefix,
            self.increment_alpha_segment(identifier),
            self.increment_numeric_segment(identifier)
        )
        return identifier

    def increment_alpha_segment(self, identifier):
        """Increments the alpha segment of the identfier."""
        alpha = self.alpha_segment(identifier)
        numeric = self.numeric_segment(identifier)
        if int(numeric) < self.max_numeric(numeric):
            return alpha
        elif int(numeric) == self.max_numeric(numeric):
            return self.increment_alpha(alpha)
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))

    def increment_numeric_segment(self, identifier):
        """Increments the numeric segment of the identifier."""
        numeric = self.numeric_segment(identifier)
        return super(AlphanumericIdentifier, self).increment(numeric)

    def alpha_segment(self, identifier):
        """Returns the alpha segment of the identifier."""
        segment = identifier[len(self.prefix):len(self.prefix) + len(self.seed[0])]
        return re.match(self.alpha_pattern, segment).group()

    def numeric_segment(self, identifier):
        """Returns the numeric segment of the partial identifier."""
        segment = identifier[
            len(self.prefix or '') + len(self.seed[0]):len(self.prefix or '') + len(self.seed[0]) + len(self.seed[1])]
        return re.match(self.numeric_pattern, segment).group()

    def increment_alpha(self, text):
        """Increments an alpha string."""
        letters = []
        letters[0:] = text.upper()
        letters.reverse()
        for index, letter in enumerate(letters):
            if ord(letter) < ord('Z'):
                letters[index] = chr(ord(letter) + 1)
                break
            else:
                letters[index] = 'A'
        letters.reverse()
        return ''.join(letters)
