from django.apps import apps as django_apps

from .exceptions import AlreadyRegistered
from edc_visit_schedule.exceptions import VisitScheduleError


class VisitSchedule:

    def __init__(self, name, app_label, enrollment_model=None, disenrollment_model=None, visit_model=None,
                 offstudy_model=None, death_report_model=None, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name or ' '.join([s.capitalize() for s in name.split('_')])
        self.app_label = app_label
        self.death_report_model = death_report_model
        self.disenrollment_model = disenrollment_model
        self.enrollment_model = enrollment_model
        self.offstudy_model = offstudy_model
        self.visit_model = visit_model
        self.schedules = {}

    def __repr__(self):
        return '<VisitSchedule(\'{}\', \'{}\')>'.format(self.name, self.app_label)

    def __str__(self):
        return self.verbose_name

    def add_schedule(self, schedule):
        """Add a schedule if not already added."""
        if schedule.name in self.schedules:
            raise AlreadyRegistered('A schedule with name {} is already registered'.format(schedule.name))
        schedule.add_enrollment_model(self.enrollment_model)
        self.validate_model_visit_schedule_name(schedule.enrollment_model)
        schedule.add_disenrollment_model(self.disenrollment_model)
        self.validate_model_visit_schedule_name(schedule.disenrollment_model)
        schedule.add_offstudy_model(self.offstudy_model)
        schedule.add_visit_model(self.visit_model)
        if self.death_report_model:
            schedule.add_death_report_model(self.death_report_model)
        self.schedules.update({schedule.name: schedule})
        return schedule

    def validate_model_visit_schedule_name(self, model):
        if model._meta.visit_schedule_name != self.name:
            raise VisitScheduleError(
                'Cannot register schedule. Model \'{}\' does not belong to this visit schedule. '
                'Got \'{}\' != \'{}\''.format(model._meta.label_lower, self.name, model._meta.visit_schedule_name))

    def get_schedule(self, value=None):
        """Return a schedule given the enrollment model label_lower."""
        try:
            _, _ = value.split('.')
            enrollment_model = django_apps.get_model(*value.split('.'))
        except ValueError:
            return self.schedules.get(value)
        except AttributeError:
            value._meta
            enrollment_model = value
        for schedule in self.schedules.values():
            if schedule.enrollment_model == enrollment_model:
                return schedule
        return None
