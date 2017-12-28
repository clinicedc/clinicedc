import re

from django.apps import apps as django_apps

from ..simple_model_validator import SimpleModelValidator
from .schedules_collection import SchedulesCollection
from edc_visit_schedule.simple_model_validator import InvalidModel


class VisitScheduleError(Exception):
    pass


class VisitScheduleNameError(Exception):
    pass


class VisitScheduleSiteError(Exception):
    pass


class VisitScheduleAppointmentModelError(Exception):
    pass


class AlreadyRegisteredSchedule(Exception):
    pass


class VisitSchedule:

    name_regex = r'[a-z0-9\_\-]+$'
    name_regex_msg = 'numbers, lower case letters and \'_\''
    schedules_collection = SchedulesCollection

    def __init__(self, name=None, verbose_name=None, previous_visit_schedule=None,
                 death_report_model=None, offstudy_model=None):
        self.name = name
        self.schedules = self.schedules_collection(visit_schedule_name=name)
        self.offstudy_model = offstudy_model
        self.death_report_model = death_report_model
        self.previous_visit_schedule = previous_visit_schedule
        if not re.match(self.name_regex, name):
            raise VisitScheduleNameError(
                f'Visit schedule name may only contain {self.name_regex_msg}. Got {name}')
        self.title = self.verbose_name = verbose_name or ' '.join(
            [s.capitalize() for s in name.split('_')])

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self.name}\')'

    def __str__(self):
        return self.name

    def check(self):
        warnings = []
        try:
            SimpleModelValidator(self.offstudy_model,
                                 f'{self.name}.offstudy_model')
        except InvalidModel as e:
            warnings.append(e)
        try:
            SimpleModelValidator(self.death_report_model,
                                 f'{self.name}.death_report_model')
        except InvalidModel as e:
            warnings.append(e)
        return warnings

    @property
    def offstudy_model_cls(self):
        return django_apps.get_model(self.offstudy_model)

    @property
    def death_report_model_cls(self):
        return django_apps.get_model(self.death_report_model)

    def add_schedule(self, schedule=None):
        """Adds a schedule, if not already added.
        """
        if schedule.name in self.schedules:
            raise AlreadyRegisteredSchedule(
                f'Schedule \'{schedule.name}\' is already registered. See \'{self}\'')
        self.schedules.update({schedule.name: schedule})
        return schedule

    def validate(self):
        try:
            self.offstudy_model_cls
            self.death_report_model_cls
        except LookupError as e:
            raise VisitScheduleError(e)
