import random
import re

from .checkdigit_mixins import LuhnOrdMixin
from .exceptions import IdentifierError
from .identifier_with_checkdigit import IdentifierWithCheckdigit
from .models import IdentifierHistory


class ShortIdentifier(LuhnOrdMixin, IdentifierWithCheckdigit):

    name = 'shortidentifier'
    allowed_chars = 'ABCDEFGHKMNPRTUVWXYZ2346789'
    checkdigit_pattern = None
    history_model = IdentifierHistory
    identifier_pattern = r'^[A-Z0-9]{5}$'
    prefix_pattern = None
    random_string_pattern = r'^[A-Z0-9]{5}$'
    seed = None
    template = '{prefix}{random_string}'

    def __init__(self, options=None):
        self.duplicate_counter = 0
        self._options = options or {}
        try:
            self.prefix = self._options['prefix']
        except KeyError:
            pass
        self.identifier = self.next_on_duplicate(None)
        super(ShortIdentifier, self).__init__(self.identifier, prefix=self.prefix)

    @property
    def options(self):
        if 'prefix' not in self._options:
            try:
                self.prefix = re.match(self.prefix_pattern[:-1], self.last_identifier).group()
                self._options.update({'prefix': self.prefix})
            except TypeError:
                self._options.update({'prefix': ''})
        return self._options

    def next_identifier(self):
        """Sets the identifier attr to the next identifier.

        Removes the checkdigit if it has one."""
        identifier_pattern = self.identifier_pattern
        if self.checkdigit_pattern:
            identifier_pattern = self.identifier_pattern[:-1] + self.checkdigit_pattern[1:]
        if self.identifier:
            if re.match(identifier_pattern, self.identifier):
                self.identifier = self.remove_checkdigit(self.identifier)
        identifier = self.remove_separator(self.identifier)
        identifier = self.increment(identifier)
        if self.checkdigit_pattern:
            checkdigit = self.calculate_checkdigit(identifier)
        else:
            checkdigit = None
        identifier = self.insert_separator(identifier, checkdigit)
        self.identifier = self.validate_identifier_pattern(
            identifier, pattern=identifier_pattern)
        self.update_history()

    def increment(self, identifier):
        """Creates a new almost unique identifier."""
        return self.next_on_duplicate(identifier)

    def next_on_duplicate(self, identifier):
        """If a duplicate, create a new identifier."""
        while True:
            self.options.update({'random_string': self.get_random_string(length=self.random_string_length)})
            identifier = self.template.format(**self.options)
            if not self.is_duplicate(identifier):
                break
            self.duplicate_counter += 1
            if self.duplicate_counter >= self.duplicate_tries:
                raise IdentifierError(
                    'Unable prepare a unique requisition identifier, '
                    'all are taken. Increase the length of the random string')
        return identifier

    @property
    def duplicate_tries(self):
        return len(self.allowed_chars) ** (self.random_string_length)

    @property
    def random_string_length(self):
        sample_string = 'A' * 100
        return len(re.match(self.random_string_pattern[:-1], sample_string).group())

    def is_duplicate(self, identifier):
        """May override with your algorithm for determining duplicates."""
        try:
            self.history_model.objects.get(identifier=identifier)
            return True
        except self.history_model.DoesNotExist:
            pass
        return False

    def get_random_string(self, length):
        """ safe for people, no lowercase and no 0OL1J5S etc."""
        return ''.join([random.choice(self.allowed_chars) for _ in range(length)])
