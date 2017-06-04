
class PrefixError(Exception):
    pass


class Prefix:

    """A class to generate an identifier prefix.
    """

    def __init__(self, template=None, length=None, **template_opts):
        try:
            self.prefix = template.format(**template_opts)
        except KeyError as e:
            raise PrefixError(f'Missing template value for \'{e}\'. Got options={template_opts}')
        if len(self.prefix) != length:
            raise PrefixError(
                f'Invalid prefix \'{self.prefix}\'. '
                f'Got length == {len(self.prefix)}. Expected {length}.')

    def __str__(self):
        return self.prefix
