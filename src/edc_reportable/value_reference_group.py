from copy import copy
from edc_base.utils import get_utcnow


GRADING = 'grading'
NORMAL = 'normal'


class InvalidValueReference(Exception):
    pass


class ValueReferenceNotFound(Exception):
    pass


class ValueReferenceAlreadyAdded(Exception):
    pass


class ValueReferenceGroup:

    def __init__(self, name=None):
        self.name = name
        self.normal_references = {}
        self.grading_references = {}
        self.error = {NORMAL: [], GRADING: []}
        self.success = {NORMAL: [], GRADING: []}
        self.grade = None

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def _add(self, value_reference, category=None):
        if category == GRADING:
            value_references = self.grading_references
        else:
            value_references = self.normal_references
        if value_reference.name != self.name:
            raise InvalidValueReference(
                f'Cannot add to group; name does not match. '
                f'Expected \'{self.name}\'. Got \'{value_reference.name}\'. '
                f'See {repr(value_reference)}')
        try:
            value_references[value_reference.gender]
        except KeyError:
            value_references[value_reference.gender] = []
        if value_reference in value_references[value_reference.gender]:
            raise ValueReferenceAlreadyAdded(
                f'Value reference {value_reference} has already been added.')
        value_references[value_reference.gender].append(value_reference)

    def add_normal(self, value_reference):
        self._add(value_reference)

    def add_grading(self, value_reference):
        self._add(value_reference, category=GRADING)

    def in_bounds(self, gender=None, dob=None, report_datetime=None, **kwargs):
        self.error[NORMAL] = []
        self.success[NORMAL] = []
        in_bounds = []
        valrefs = self.get_value_references(
            gender=gender,
            dob=dob,
            report_datetime=report_datetime or get_utcnow())
        if not valrefs:
            in_bounds = [True]
        for valref in valrefs:
            in_bounds.append(valref.in_bounds(**kwargs))
            self.error[NORMAL].append(valref)
            self.success[NORMAL].append(valref)
        return any(in_bounds)

    def in_bounds_for_grade(self, gender=None, dob=None, report_datetime=None, **kwargs):
        self.error[GRADING] = []
        self.success[GRADING] = []
        in_bounds = []
        self.grade = None
        grade_refs = self.get_value_references(
            gender=gender,
            dob=dob,
            report_datetime=report_datetime or get_utcnow(),
            category=GRADING)
        if grade_refs:
            grade_refs.sort(key=lambda x: x.grade, reverse=True)
            for grade_ref in grade_refs:
                in_bounds.append(grade_ref.in_bounds(**kwargs))
                if grade_ref.error:
                    self.error[GRADING].append(grade_ref)
                if grade_ref.success:
                    self.success[GRADING].append(grade_ref)
                try:
                    self.grade = self.success[GRADING][0].grade
                except IndexError:
                    self.grade = None
        return any(in_bounds)

    def get_value_references(self, gender=None, dob=None, report_datetime=None, category=None):
        references = []
        if category == GRADING:
            value_references = self.grading_references
        else:
            value_references = self.normal_references
        for refs in value_references.values():
            references.extend(
                [ref for ref in refs if gender in ref.gender])
        for ref in copy(references):
            if not ref.age_match(dob, report_datetime):
                index = references.index(ref)
                references.pop(index)
        return references
