class Fieldlist:
    def __init__(
        self, insert_fields=None, remove_fields=None, insert_after=None, section=None, **kwargs
    ):
        self.insert_fields = insert_fields
        self.remove_fields = remove_fields
        self.insert_after = insert_after
        self.section = section


class Remove:
    def __init__(self, *fields, section=None, **kwargs):
        self.remove_fields = fields
        self.section = section


class Insert:
    def __init__(self, *fields, after=None, section=None, **kwargs):
        self.insert_fields = fields
        self.insert_after = after
        self.section = section
