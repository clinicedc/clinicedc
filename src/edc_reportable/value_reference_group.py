from edc_base.utils import get_utcnow
from edc_reportable.evaluator import ValueBoundryError
from copy import copy


class InvalidValueReference(Exception):
    pass


class ValueReferenceNotFound(Exception):
    pass


class ValueReferenceAlreadyAdded(Exception):
    pass


class ValueReferenceGroup:

    def __init__(self, name=None):
        self.name = name
        self.references = {}
        self.error = []
        self.success = []

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def add(self, value_reference):
        if value_reference.name != self.name:
            raise InvalidValueReference(
                f'Cannot add to group; name does not match. '
                f'Expected \'{self.name}\'. Got \'{value_reference.name}\'. '
                f'See {repr(value_reference)}')
        try:
            self.references[value_reference.gender]
        except KeyError:
            self.references[value_reference.gender] = []
        if value_reference in self.references[value_reference.gender]:
            raise ValueReferenceAlreadyAdded(
                f'Value reference {value_reference} has already been added.')
        self.references[value_reference.gender].append(value_reference)

    def in_bounds(self, gender=None, dob=None, report_datetime=None, **kwargs):
        self.error = []
        self.success = []
        in_bounds = []
        valrefs = self.get_value_references(
            gender=gender,
            dob=dob,
            report_datetime=report_datetime or get_utcnow())
        if not valrefs:
            in_bounds = [True]
        for valref in valrefs:
            in_bounds.append(valref.in_bounds(**kwargs))
            self.error.append(valref.error)
            self.success.append(valref.success)
        return any(in_bounds)

    def get_value_references(self, gender=None, dob=None, report_datetime=None):
        references = []
        for refs in self.references.values():
            references.extend([ref for ref in refs if gender == ref.gender])
        for ref in copy(references):
            if not ref.age_match(dob, report_datetime):
                index = references.index(ref)
                references.pop(index)
        return references
