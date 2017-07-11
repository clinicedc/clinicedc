import re

from django.apps import apps as django_apps

from ..visit_schedule import SchedulesCollectionError
from .models_collection import ModelsCollection
from .schedules_collection import SchedulesCollection
from pprint import pprint


class VisitScheduleError(Exception):
    pass


class VisitScheduleNameError(Exception):
    pass


class VisitScheduleSiteError(Exception):
    pass


class AlreadyRegisteredSchedule(Exception):
    pass


class VisitSchedule:

    name_regex = r'[a-z0-9\_\-]+$'
    name_regex_msg = 'numbers, lower case letters and \'_\''
    schedules_collection = SchedulesCollection
    models_collection = ModelsCollection

    def __init__(self, name=None, verbose_name=None, previous_visit_schedule=None,
                 enrollment_model=None, disenrollment_model=None,
                 visit_model=None, death_report_model=None, offstudy_model=None,
                 **kwargs):
        self.models = self.models_collection(visit_schedule_name=name)
        self.name = name
        self.schedules = self.schedules_collection(visit_schedule_name=name)
        self.visit_model = visit_model
        self.previous_visit_schedule = previous_visit_schedule
        if not re.match(self.name_regex, name):
            raise VisitScheduleNameError(
                f'Visit schedule name may only contain {self.name_regex_msg}. Got {name}')
        self.title = self.verbose_name = verbose_name or ' '.join(
            [s.capitalize() for s in name.split('_')])
        self.models.update(enrollment_model=enrollment_model)
        self.models.update(disenrollment_model=disenrollment_model)
        self.models.update(visit_model=visit_model)
        self.models.update(death_report_model=death_report_model)
        self.models.update(offstudy_model=offstudy_model)

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self.name}\')'

    def __str__(self):
        return self.name

    @property
    def visit_model_cls(self):
        return django_apps.get_model(self.visit_model)

    def get_schedule(self, **kwargs):
        """Returns a schedule instance or raises.
        """
        try:
            return self.schedules.get_schedule(**kwargs)
        except SchedulesCollectionError as e:
            raise VisitScheduleError(e) from e

    def get_schedules(self, schedule_name=None, **kwargs):
        """Returns a dictionary of schedules.
        """
        if schedule_name:
            schedules = {
                schedule_name: self.get_schedule(schedule_name=schedule_name, **kwargs)}
        else:
            schedules = self.schedules
        return schedules

    def add_schedule(self, schedule=None):
        """Adds a schedule, if not already added.

        Note: Meta (visit_schedule_name.schedule_name) on enroll/disenrollment models must
        match this object's visit_schedule_name.
        """
        if schedule.name in self.schedules:
            raise AlreadyRegisteredSchedule(
                f'Schedule \'{schedule.name}\' is already registered. See \'{self}\'')
        schedule.enrollment_model = (
            schedule.enrollment_model or self.models.enrollment_model)
        schedule.disenrollment_model = (
            schedule.disenrollment_model or self.models.disenrollment_model)
        self.schedules.update({schedule.name: schedule})
        return schedule

    def validate(self):
        self.models.validate()
        self.schedules.validate()
