import re

from django.apps import apps as django_apps
from django.conf import settings
from edc_base import get_utcnow

from ..subject_schedule import SubjectSchedule
from ..validator import Validator, ValidatorLookupError
from ..visit import Visit
from .visit_collection import VisitCollection


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

    Contains an ordered dictionary of visit instances and the onschedule
    and offschedule models used to get on and off the schedule.
    """
    name_regex = r'[a-z0-9\_\-]+$'
    visit_cls = Visit
    visit_collection_cls = VisitCollection
    model_validator_cls = Validator
    subject_schedule_cls = SubjectSchedule

    def __init__(self, name=None, title=None, sequence=None, onschedule_model=None,
                 offschedule_model=None, validate=None, appointment_model=None,
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
        if not onschedule_model:
            raise ScheduleModelError('Invalid onschedule model. Got None')
        self.onschedule_model = onschedule_model.lower()
        if not offschedule_model:
            raise ScheduleModelError('Invalid offschedule model. Got None')
        self.offschedule_model = offschedule_model.lower()
        self.appointment_model = appointment_model
        if not self.appointment_model:
            try:
                self.appointment_model = settings.DEFAULT_APPOINTMENT_MODEL
            except AttributeError:
                self.appointment_model = 'edc_appointment.appointment'
            if not self.appointment_model:
                raise ScheduleAppointmentModelError(
                    f'Invalid appointment model for schedule {repr(self)}. '
                    f'Got None. Either declare on the Schedule or in '
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
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def offschedule_model_cls(self):
        return django_apps.get_model(self.offschedule_model)

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
        """Raises an exception if onschedule/offschedule models
        are invalid.
        """
        try:
            self.model_validator_cls(
                model=self.onschedule_model,
                schedule_name=self.name,
                visit_schedule_name=visit_schedule_name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')

        try:
            self.model_validator_cls(
                model=self.offschedule_model,
                schedule_name=self.name,
                visit_schedule_name=visit_schedule_name).validated_model
        except ValidatorLookupError as e:
            raise ScheduleModelError(f'{repr(self)} raised {e}')

    def put_on_schedule(self, onschedule_datetime=None, **kwargs):
        """Puts a subject onto this schedule.
        """
        onschedule_datetime = onschedule_datetime or get_utcnow()
        subject_schedule = self.subject_schedule_cls(
            onschedule_model=self.onschedule_model, **kwargs)
        subject_schedule.put_on_schedule(
            onschedule_datetime=onschedule_datetime)

    def refresh_schedule(self, **kwargs):
        """Resaves the onschedule model to, for example, refresh
        appointments.
        """
        subject_schedule = self.subject_schedule_cls(
            onschedule_model=self.onschedule_model, **kwargs)
        subject_schedule.resave()

    def take_off_schedule(self, offschedule_datetime=None, subject_identifier=None, **kwargs):
        """Takes a subject off of this schedule and deletes any
        appointments with appt_datetime after the offschedule datetime.
        """
        offschedule_datetime = offschedule_datetime or get_utcnow()
        subject_schedule = self.subject_schedule_cls(
            subject_identifier=subject_identifier,
            onschedule_model=self.onschedule_model, **kwargs)
        subject_schedule.take_off_schedule(
            offschedule_model=self.offschedule_model,
            offschedule_datetime=offschedule_datetime)
        appointment_model_cls = django_apps.get_model(self.appointment_model)
        appointment_model_cls.objects.delete_for_subject_after_date(
            subject_identifier, offschedule_datetime)
