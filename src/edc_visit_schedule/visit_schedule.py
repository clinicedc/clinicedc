from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.membership_form import MembershipForm

from .exceptions import AlreadyRegistered, VisitScheduleError


class VisitSchedule:

    def __init__(self, name, app_label):
        self.name = name
        self.app_label = app_label
        self.schedules = {}
        self.membership_forms = {}

    def __str__(self):
        return self.name

    def add_schedule(self, schedule_name, grouping_key=None):
        """Add a schedule if not already added."""
        schedule = Schedule(name=schedule_name, grouping_key=grouping_key)
        if schedule_name in self.schedules:
            raise AlreadyRegistered('A schedule with name {} is already registered'.format(schedule_name))
        self.schedules.update({schedule_name: schedule})
        try:
            self.membership_forms[schedule_name]
        except KeyError:
            self.membership_forms[schedule_name] = {}

    def add_membership_form(self, schedule_name, **kwargs):
        """Add a membership form if not already added."""
        if not self.schedules.get(schedule_name):
            raise VisitScheduleError('Membership form refers to non-existent schedule. Got {}'.format(schedule_name))
        membership_form = MembershipForm(**kwargs)
        if membership_form.name in self.membership_forms[schedule_name]:
            raise AlreadyRegistered('Membership form already registered. Got {}'.format(membership_form))
        self.membership_forms[schedule_name].update({membership_form.name: membership_form})

    def add_visit(self, schedule_name, code, visit_model, **kwargs):
        """Add a visit to an existing schedule."""
        schedule = self.schedules.get(schedule_name)
        if not schedule:
            raise VisitScheduleError('Schedule does not exist. Got {}.'.format(schedule_name))
        visit = schedule.add_visit(code, visit_model, **kwargs)
        self.schedules.update(schedule_name=schedule)
        return visit

    def get_membership_form(self, app_label, model_name, schedule_name=None):
        """Return a MembershipForm class from the visit_schedule or None."""
        membership_form = {}
        membership_forms = []
        for mf in self.membership_forms.get(schedule_name, self.membership_forms).values():
            if mf.get('{}.{}'.format(app_label, model_name)):
                membership_forms.append(mf)
        if len(membership_forms) > 1:
            raise VisitScheduleError(
                'Multiple membership forms returned. Try specifying '
                'the schedule_name. Got {}, {}, schedule_name={}'.format(app_label, model_name, schedule_name))
        elif len(membership_forms) == 1:
            membership_form = membership_forms[0]
        else:
            membership_form = {}
        return membership_form.get('{}.{}'.format(app_label, model_name))
