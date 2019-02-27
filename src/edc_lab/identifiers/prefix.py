class PrefixLengthError(Exception):
    pass


class PrefixKeyError(Exception):
    pass


class Prefix:

    """A class to generate an identifier prefix.
    """

    template = "{protocol_number}{requisition_identifier}"
    length = 10

    def __init__(self, template=None, length=None, **template_opts):
        self.template = template or self.template
        self.length = length or self.length
        template_opts = {k: v for k, v in template_opts.items() if v is not None}
        try:
            self.prefix = self.template.format(**template_opts)
        except KeyError as e:
            raise PrefixKeyError(
                f"Missing template value for '{e}'. Got options={template_opts}"
            )
        if len(self.prefix) != self.length:
            raise PrefixLengthError(
                f"Invalid prefix '{self.prefix}'. "
                f"Got length == {len(self.prefix)}. Expected {self.length}."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.template}, {self.length})"

    def __str__(self):
        return self.prefix
