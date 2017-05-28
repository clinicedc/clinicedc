import re

from ..models_validator.validator import Validator, ValidatorLookupError
from ..visit import Visit
from .visit_collection import VisitCollection


class ScheduleModelError(Exception):
    pass


class ScheduleNameError(Exception):
    pass


class AlreadyRegisteredVisit(Exception):
    pass


class Schedule:

    """A class that represents a "schedule" of visits.

    Is contained by a "visit schedule".

    Contains an ordered dictionary of visit instances and the enrollment
    and disenrollment models used to get on and off the schedule.
    """

    name_regex = r'[a-z0-9\_\-]+$'
    visit_cls = Visit
    visit_collection_cls = VisitCollection
    model_validator_cls = Validator

    def __init__(self, name=None, title=None, sequence=None, enrollment_model=None,
                 disenrollment_model=None, **kwargs):
        self.visits = self.visit_collection_cls()
        if not name or not re.match(r'[a-z0-9\_\-]+$', name):
            raise ScheduleNameError(
                f'Invalid name. Got \'{name}\'. May only contains numbers, '
                'lower case letters and \'_\'.')
        else:
            self.name = name
        self.title = title or name
        self.sequence = sequence or name

        try:
            self.enrollment_model = self.model_validator_cls(
                model=enrollment_model,
                schedule_name=self.name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')

        try:
            self.disenrollment_model = self.model_validator_cls(
                model=disenrollment_model,
                schedule_name=self.name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')

    def __repr__(self):
        return f'Schedule({self.name})'

    def __str__(self):
        return self.name

    @property
    def field_value(self):
        return self.name

    def add_visit(self, visit=None, **kwargs):
        """Adds a unique visit to the schedule.
        """
        visit = visit or self.visit_cls(**kwargs)
        for attr in ['code', 'title', 'timepoint', 'rbase']:
            if getattr(visit, attr) in [getattr(v, attr) for v in self.visits.values()]:
                raise AlreadyRegisteredVisit(
                    f'Visit already registered. Got visit={visit} ({attr}). '
                    f'See schedule \'{self}\'')
        self.visits.update({visit.code: visit})
        return visit
