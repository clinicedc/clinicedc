import re

from django.apps import apps as django_apps

from ..validator import Validator, ValidatorLookupError
from ..visit import Visit
from .visit_collection import VisitCollection
from django.conf import settings


class ScheduleModelError(Exception):
    pass


class ScheduleAppointmentModelError(Exception):
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
                 disenrollment_model=None, validate=None, appointment_model=None,
                 **kwargs):
        self.visits = self.visit_collection_cls()
        if not name or not re.match(r'[a-z0-9\_\-]+$', name):
            raise ScheduleNameError(
                f'Invalid name. Got \'{name}\'. May only contains numbers, '
                'lower case letters and \'_\'.')
        else:
            self.name = name
        self.title = title or name
        self.sequence = sequence or name
        if not enrollment_model:
            raise ScheduleModelError('Invalid enrollment model. Got None')
        self.enrollment_model = enrollment_model.lower()
        if not disenrollment_model:
            raise ScheduleModelError('Invalid disenrollment model. Got None')
        self.disenrollment_model = disenrollment_model.lower()
        self.appointment_model = appointment_model
        if not self.appointment_model:
            try:
                self.appointment_model = settings.DEFAULT_APPOINTMENT_MODEL
            except AttributeError:
                self.appointment_model = 'edc_appointment.appointment'
            if not self.appointment_model:
                raise ScheduleAppointmentModelError(
                    f'Invalid appointment model for schedule {repr(self)}. Got None. '
                    f'Either declare on the Schedule or in '
                    f'settings.DEFAULT_APPOINTMENT_MODEL.')

        if validate:
            self.validate()

    def __repr__(self):
        return f'Schedule({self.name})'

    def __str__(self):
        return self.name

    @property
    def field_value(self):
        return self.name

    @property
    def enrollment_model_cls(self):
        return django_apps.get_model(self.enrollment_model)

    @property
    def disenrollment_model_cls(self):
        return django_apps.get_model(self.disenrollment_model)

    def add_visit(self, visit=None, **kwargs):
        """Adds a unique visit to the schedule.
        """
        visit = visit or self.visit_cls(**kwargs)
        for attr in ['code', 'title', 'timepoint', 'rbase']:
            if getattr(visit, attr) in [getattr(v, attr) for v in self.visits.values()]:
                raise AlreadyRegisteredVisit(
                    f'Visit already registered. Got visit={visit} ({attr}). '
                    f'See schedule \'{self}\'')
        if not visit.appointment_model:
            visit.appointment_model = self.appointment_model
        self.visits.update({visit.code: visit})
        return visit

    def validate(self, visit_schedule_name=None):
        """Raises an exception if enrollment/disenrollment models
        are invalid.
        """
        try:
            self.model_validator_cls(
                model=self.enrollment_model,
                schedule_name=self.name,
                visit_schedule_name=visit_schedule_name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')

        try:
            self.model_validator_cls(
                model=self.disenrollment_model,
                schedule_name=self.name,
                visit_schedule_name=visit_schedule_name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')
