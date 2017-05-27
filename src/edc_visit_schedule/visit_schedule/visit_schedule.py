import re

from .model_validator import ModelValidator, ModelValidatorError
from .model_validator import EnrollmentModelValidator, DisenrollmentModelValidator
from .model_validator import EnrollmentModelValidatorError
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
    model_validator_cls = ModelValidator
    enrollment_model_validator = EnrollmentModelValidator
    disenrollment_model_validator = DisenrollmentModelValidator
    schedules_collection = SchedulesCollection

    def __init__(self, name=None, app_label=None,
                 verbose_name=None, previous_visit_schedule=None, **kwargs):
        self.name = name
        self.schedules = SchedulesCollection()
        self.previous_visit_schedule = previous_visit_schedule
        if not re.match(self.name_regex, name):
            raise VisitScheduleNameError(
                f'Visit schedule name may only contain {self.name_regex_msg}. Got {name}')
        self.app_label = app_label
        self.title = self.verbose_name = verbose_name or ' '.join(
            [s.capitalize() for s in name.split('_')])
        try:
            self.models = self.model_validator_cls(
                visit_schedule_name=self.name, **kwargs)
        except (ModelValidatorError, EnrollmentModelValidatorError) as e:
            raise VisitScheduleModelError(e) from e

    def __repr__(self):
        return f'{self.__class__.__name__}(\'{self.name}\')'

    def __str__(self):
        return self.name

    def get_schedule(self, **kwargs):
        return self.schedules.get_schedule(**kwargs)

    def get_schedule_by_model(self, **kwargs):
        return self.schedules.get_schedule_by_model(**kwargs)

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
        try:
            schedule.enrollment_model = self.enrollment_model_validator(
                model=schedule.enrollment_model or self.models.enrollment_model,
                visit_schedule_name=self.name).model
        except EnrollmentModelValidatorError as e:
            raise VisitScheduleModelError(e) from e
        try:
            schedule.disenrollment_model = self.disenrollment_model_validator(
                model=schedule.disenrollment_model or self.models.disenrollment_model,
                visit_schedule_name=self.name).model
        except EnrollmentModelValidatorError as e:
            raise VisitScheduleModelError(e) from e
        self.schedules.update({schedule.name: schedule})
        return schedule
