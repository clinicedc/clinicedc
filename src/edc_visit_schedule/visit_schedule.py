from collections import OrderedDict
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.membership_form import MembershipForm

from .exceptions import AlreadyRegistered, VisitScheduleError


class VisitSchedule:

    def __init__(self, name, app_label):
        self.name = name
        self.app_label = app_label
        self.schedules = OrderedDict()
        self.membership_forms = OrderedDict()

    def __str__(self):
        return self.name

    def add_schedule(self, schedule_name, grouping_key=None):
        """Add a schedule if not already added."""
        schedule = Schedule(name=schedule_name, grouping_key=grouping_key)
        if schedule_name in self.schedules:
            raise AlreadyRegistered('A schedule with name {} is already registered'.format(schedule_name))
        self.schedules.update(name=schedule)
        try:
            self.membership_forms[schedule_name]
        except KeyError:
            self.membership_forms[schedule_name] = {}

    def add_membership_form(self, schedule_name, **kwargs):
        """Add a membership form if not already added."""
        if not self.schedules.get(schedule_name):
            raise VisitScheduleError('Membership form refers to non-existent schedule. Got {}'.format(schedule_name))
        membership_form = MembershipForm(**kwargs)
        self.membership_forms[schedule_name].update({membership_form.name: membership_form})

    def add_visits(self, schedule_name, code, **kwargs):
        """Add a visit to an existing schedule."""
        schedule = self.schedules.get(schedule_name)
        schedule.add_visit(code, **kwargs)
        self.schedules.update(schedule_name=schedule)

    def add_visit_definitions(self, schedule_name, code, **kwargs):
        return self.add_visits(schedule_name, code, **kwargs)

    def get_membership_form(self, app_label, model_name):
        membership_form = None
        for membership_form in self.membership_forms.values():
            if membership_form.app_label == app_label and membership_form.model_name == model_name:
                break
        return membership_form
