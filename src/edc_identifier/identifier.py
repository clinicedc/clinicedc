import re

from .exceptions import IdentifierError
from .models import IdentifierHistory


class Identifier(object):

    name = 'identifier'
    history_model = IdentifierHistory
    identifier_pattern = '^\d+$'
    prefix_pattern = None
    prefix = None
    seed = ['0']
    separator = None

    def __init__(self, last_identifier=None, prefix=None):
        self.identifier_as_list = []
        self.prefix = prefix or self.prefix or ''
        try:
            seed = ''.join(self.seed)
        except TypeError:
            seed = self.seed
        self.identifier = last_identifier or self.last_identifier or '{}{}'.format(self.prefix, seed)
        self.prefix_pattern = r'^{}$'.format(self.prefix)
        self.identifier_pattern = self.prefix_pattern[:-1] + self.identifier_pattern[1:]
        if self.identifier:
            self.validate_identifier_pattern(self.identifier)
        self.next_identifier()

    def __repr__(self):
        return '{0.__name__}(\'{1}\')'.format(self.__class__, self.identifier)

    def __str__(self):
        return self.identifier

    def __next__(self):
        self.next_identifier()
        return self.identifier

    def next(self):
        return self.__next__()

    def next_identifier(self):
        """Sets the next identifier and updates the history."""
        while True:
            identifier = self.remove_separator(self.identifier)
            identifier = self.increment(identifier)
            self.identifier = self.insert_separator(identifier)
            self.validate_identifier_pattern(self.identifier)
            if self.update_history():
                break

    def increment(self, identifier):
        return str(int(identifier or 0) + 1)

    def validate_identifier_pattern(self, identifier, pattern=None, error_msg=None):
        pattern = pattern or self.identifier_pattern
        try:
            identifier = re.match(pattern, identifier).group()
        except AttributeError:
            error_msg = error_msg or 'Invalid identifier format for pattern {}. Got {}'.format(
                pattern, identifier)
            raise IdentifierError(error_msg)
        return identifier

    @property
    def identifier_prefix(self):
        """Returns the prefix extracted from the identifier using the prefix_pattern."""
        if not self.prefix_pattern:
            return None
        return re.match(self.prefix_pattern[:-1], self.identifier).group()

    def update_history(self):
        """Attempts to update history and returns True (or instance) if successful else False if
        identifier already exists."""
        if self.history_model:
            try:
                self.history_model.objects.get(identifier=self.identifier)
                return False
            except self.history_model.DoesNotExist:
                return self.history_model.objects.create(
                    identifier=self.identifier,
                    identifier_type=self.name,
                    identifier_prefix=self.identifier_prefix)
        return True

    @property
    def last_identifier(self):
        """Returns the last identifier in the history model."""
        try:
            instance = self.history_model.objects.filter(
                identifier_type=self.name
            ).last()
            return instance.identifier
        except AttributeError:
            return None

    def remove_separator(self, identifier):
        """Returns the identifier after removing the separator.

        The identifier is split into a list by separator and saved  as `identifier_as_list`."""
        if not identifier:
            return identifier
        else:
            self.identifier_as_list = identifier.split(self.separator)
            return ''.join(self.identifier_as_list)

    def insert_separator(self, identifier):
        """Returns the identifier by reinserting the separator."""
        if not self.identifier_as_list:
            self.identifier_as_list = [identifier]
        start = 0
        items = []
        for item in self.identifier_as_list:
            items.append(identifier[start:start + len(item)])
            start += len(item)
        identifier = (self.separator or '').join(items)
        return identifier
