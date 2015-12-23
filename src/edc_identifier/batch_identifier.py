import re

from datetime import datetime

from .identifier import Identifier


class BatchIdentifier(Identifier):

    """Manages a sequential identifier prefixed by the current date stamp."""

    name = 'batchidentifier'
    identifier_pattern = r'^[0-9]{4}$'
    prefix_pattern = r'^[0-9]{8}$'
    seed = ['0000']

    def __init__(self, last_identifier=None):
        if not last_identifier:
            prefix = datetime.today().strftime('%Y%m%d')
            last_identifier = '{}{}'.format(prefix, ''.join(self.seed))
        else:
            prefix = re.match(self.prefix_pattern[:-1], last_identifier).group()
        super(BatchIdentifier, self).__init__(last_identifier, prefix=prefix)
