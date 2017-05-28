import re

from ..models_validator import Validator, ValidatorLookupError
from ..visit_schedule import SchedulesCollectionError
from .schedules_collection import SchedulesCollection


class VisitScheduleError(Exception):
    pass


class VisitScheduleNameError(Exception):
    pass


class VisitScheduleModelError(Exception):
    pass


class VisitScheduleSiteError(Exception):
    pass


class AlreadyRegisteredSchedule(Exception):
    pass


class VisitSchedule:

    name_regex = r'[a-z0-9\_\-]+$'
    name_regex_msg = 'numbers, lower case letters and \'_\''
    model_validator_cls = Validator
    enrollment_required_fields = [
        'report_datetime', 'visit_schedule_name', 'schedule_name']
    schedules_collection = SchedulesCollection

    def __init__(self, name=None, verbose_name=None, previous_visit_schedule=None,
                 enrollment_model=None, disenrollment_model=None,
                 visit_model=None, death_report_model=None, offstudy_model=None, **kwargs):
        self.models = {}
        self.name = name
        self.schedules = SchedulesCollection()
        self.previous_visit_schedule = previous_visit_schedule
        if not re.match(self.name_regex, name):
            raise VisitScheduleNameError(
                f'Visit schedule name may only contain {self.name_regex_msg}. Got {name}')
        self.title = self.verbose_name = verbose_name or ' '.join(
            [s.capitalize() for s in name.split('_')])

        if enrollment_model:
            try:
                model = self.model_validator_cls(
                    model=enrollment_model,
                    visit_schedule_name=self.name,
                    required_fields=self.enrollment_required_fields).validated_model
            except ValidatorLookupError as e:
                raise VisitScheduleModelError(f'{repr(self)} raised {e}')
            else:
                self.models.update(enrollment_model=model)

        if disenrollment_model:
            try:
                model = self.model_validator_cls(
                    model=disenrollment_model,
                    visit_schedule_name=self.name,
                    required_fields=self.enrollment_required_fields).validated_model
            except ValidatorLookupError as e:
                raise VisitScheduleModelError(f'{repr(self)} raised {e}')
            else:
                self.models.update(disenrollment_model=model)

        if visit_model:
            self.models.update(visit_model=self.model_validator_cls(
                model=visit_model).validated_model)
        if death_report_model:
            self.models.update(death_report_model=self.model_validator_cls(
                model=death_report_model).validated_model)
        if offstudy_model:
            self.models.update(offstudy_model=self.model_validator_cls(
                model=offstudy_model).validated_model)

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self.name}\')'

    def __str__(self):
        return self.name

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

    def add_schedule(self, schedule):
        """Adds a schedule, if not already added.

        Note: Meta (visit_schedule_name.schedule_name) on enroll/disenrollment models must
        match this object's visit_schedule_name.
        """
        if schedule.name in self.schedules:
            raise AlreadyRegisteredSchedule(
                f'Schedule \'{schedule.name}\' is already registered. See \'{self}\'')
        schedule.enrollment_model = (
            schedule.enrollment_model or self.models.enrollment_model)
        schedule.enrollment_model = self.model_validator_cls(
            model=schedule.enrollment_model,
            visit_schedule_name=self.name).validated_model
        schedule.disenrollment_model = (
            schedule.disenrollment_model or self.models.disenrollment_model)
        schedule.disenrollment_model = self.model_validator_cls(
            model=schedule.disenrollment_model,
            visit_schedule_name=self.name).validated_model
        self.schedules.update({schedule.name: schedule})
        return schedule
