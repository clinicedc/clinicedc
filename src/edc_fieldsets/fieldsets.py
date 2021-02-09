import copy
from collections import OrderedDict


class FieldsetError(Exception):
    pass


class Fieldsets:

    """A class to use with model admin fieldsets."""

    def __init__(self, fieldsets=None, **kwargs):
        self.fieldsets_asdict = OrderedDict(copy.deepcopy(fieldsets))

    @property
    def fieldsets(self):
        return tuple([(k, v) for k, v in self.fieldsets_asdict.items()])

    def move_to_end(self, sections):
        if sections:
            for section in sections:
                self.fieldsets_asdict.move_to_end(section)

    def add_fieldset(self, section=None, fields=None, fieldset=None):
        """Adds a fieldset to the given section/fields or fieldset.

        * fieldset: a Fieldset class instance.
        """
        if fieldset:
            section = fieldset.fieldset[0]
            fields = fieldset.fieldset[1]["fields"]
        self.fieldsets_asdict.update({section: {"fields": fields}})

    def add_fieldsets(self, fieldsets=None):
        """Adds a list of fieldsets."""
        try:
            fieldsets[0]
        except TypeError:
            fieldsets = [fieldsets]
        for fieldset in fieldsets:
            section = fieldset.fieldset[0]
            fields = fieldset.fieldset[1]["fields"]
            self.fieldsets_asdict.update({section: {"fields": fields}})

    def insert_fields(self, *insert_fields, insert_after=None, section=None):
        """Inserts fields after insert_after in the given section."""
        if insert_fields and insert_fields != (None,):
            fields = self._copy_section_fields(section)
            position = self._get_field_position(fields, insert_after)
            for index, field in enumerate(insert_fields):
                fields.insert(index + position, field)
            self.fieldsets_asdict[section]["fields"] = tuple(fields)

    def remove_fields(self, *remove_fields, section=None):
        """Removes fields from the given section."""
        if remove_fields and remove_fields != (None,):
            fields = self._copy_section_fields(section)
            fields = [f for f in fields if f not in remove_fields]
            self.fieldsets_asdict[section]["fields"] = tuple(fields)

    def _copy_section_fields(self, section):
        """Returns fields as a list which is a copy of the fields
        tuple in a section or raises if section does not exist.
        """
        try:
            fields = copy.copy(self.fieldsets_asdict[section]["fields"])
        except KeyError:
            raise FieldsetError("Invalid fieldset section. Got {}".format(section))
        return list(fields)

    @staticmethod
    def _get_field_position(fields, insert_after):
        try:
            position = fields.index(insert_after) + 1
        except ValueError:
            raise FieldsetError(
                f"Field does not exist in section {fields}. Got {insert_after}"
            )
        return position
