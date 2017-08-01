
class AliquotIdentifierLengthError(Exception):
    pass


class AliquotIdentifierCountError(Exception):
    pass


class AliquotIdentifier:

    template = '{identifier_prefix}{parent_segment}{numeric_code}{count}'

    def __init__(self, identifier_length=None, identifier_prefix=None, parent_segment=None,
                 numeric_code=None, count=None, count_padding=None, ** kwargs):
        """
        A class to generate aliquot identifiers:

        Keyword args:
            * length: overall length of identifier
            * identifier_prefix: a prefix as string
            * child_segment: 4 digit segment. `None` if primary.
            * numeric_code: aliquot type numeric code (2 digits segment)
            * count: sequence in aliquoting history relative to primary. (01 for primary)
            * count_padding: zfill padding.
        """

        if parent_segment:
            self.is_primary = False
            if not count or count <= 1:
                raise AliquotIdentifierCountError(
                    f'Unknown aliquot number/count. Expected a number '
                    f'greater than 1. Got {count}.')
        else:
            self.is_primary = True
            parent_segment = '0000'
            count = 1

        options = dict(
            identifier_prefix=identifier_prefix or '',
            parent_segment=parent_segment,
            numeric_code=numeric_code or '',
            count=str(count).zfill(count_padding or 0)
        )

        self.identifier = self.template.format(**options)

        if len(self.identifier) != identifier_length:
            raise AliquotIdentifierLengthError(
                f'Invalid length. Expected {identifier_length}. '
                f'Got len({self.identifier})=={len(self.identifier)}.')

    def __str__(self):
        return self.identifier
