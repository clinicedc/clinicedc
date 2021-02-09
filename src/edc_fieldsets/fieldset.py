class Fieldset:

    """ "A class to format a fieldset."""

    def __init__(self, *fields, section=None):
        self.fieldset = (section, {"fields": fields})
