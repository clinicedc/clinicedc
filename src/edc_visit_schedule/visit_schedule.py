from django.apps import apps as django_apps

from .exceptions import AlreadyRegistered


class VisitSchedule:

    def __init__(self, name, app_label, visit_model=None, off_study_model=None,
                 death_report_model=None, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name or ' '.join([s.capitalize() for s in name.split('_')])
        self.app_label = app_label
        self.visit_model = visit_model
        self.off_study_model = off_study_model
        self.death_report_model = death_report_model
        self.schedules = {}

    def __str__(self):
        return self.verbose_name

    def add_schedule(self, schedule):
        """Add a schedule if not already added."""
        if schedule.name in self.schedules:
            raise AlreadyRegistered('A schedule with name {} is already registered'.format(schedule.name))
        schedule.visit_model = self.visit_model
        self.schedules.update({schedule.name: schedule})
        return schedule

#     def add_visit(self, schedule_name, code, **kwargs):
#         """Add a visit to an existing schedule."""
#         try:
#             schedule = self.schedules[schedule_name]
#         except KeyError:
#             raise VisitScheduleError('Failed to add visit. Schedule does not exist. Got {}.'.format(schedule_name))
#         visit = schedule.add_visit(code, **kwargs)
#         self.schedules.update({schedule.name: schedule})
#         return visit

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
