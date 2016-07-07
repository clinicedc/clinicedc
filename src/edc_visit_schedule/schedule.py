from edc_visit_schedule.visit import Visit
from dateutil.relativedelta import relativedelta
from edc_visit_schedule.exceptions import AlreadyRegistered, ScheduleError, CrfError


class Schedule:
    def __init__(self, name, visit_model=None, off_study_model=None, death_report_model=None, grouping_key=None):
        self.name = name
        self.visit_model = visit_model
        self.visits = {}
        # may specify a common value to group a number of membership forms so '
        # that when one of the group is keyed, the others are no longer shown.'
        self.grouping_key = grouping_key
        self.off_study_model = off_study_model
        self.death_report_model = death_report_model

    def __str__(self):
        return self.name

    @property
    def group_name(self):
        return self.name

    def add_visit(self, code, visit_model, **kwargs):
        visit = Visit(code, visit_model or self.visit_model, self.name, **kwargs)
        if visit.code in self.visits:
            raise AlreadyRegistered(
                'Visit is already registered with schedule \'{}\'. Got {}'.format(self.name, visit))
        if visit.time_point in [v.time_point for v in self.visits.values()]:
            raise ScheduleError(
                'Visit with time_point \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.time_point, self.name, visit))
        if visit.base_interval in [v.base_interval for v in self.visits.values()]:
            raise ScheduleError(
                'Visit with base_interval \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.base_interval, self.name, visit))
        if kwargs.get('crfs'):
            show_orders = sorted([crf.show_order for crf in kwargs.get('crfs')])
            if len(list(set(show_orders))) != len(show_orders):
                raise CrfError(
                    'Crf show order must be a unique sequence. Got {} in schedule {}'.format(show_orders, self.name))
        self.visits.update({code: visit})
        return visit

    def get_visits_by_visit_model(self, visit_model):
        """Returns a list of visits declared with the given visit model."""
        return [v for v in self.visits.values()
                if (v.visit_model._meta.app_label == visit_model._meta.app_label and
                    v.visit_model._meta.model_name == visit_model._meta.model_name)]

    def get_previous_visit(self, code, visit_model=None):
        """Returns the previous visit or None."""
        # ordering was by ('time_point', 'base_interval')
        CODE = 1
        if visit_model:
            visits = self.get_visits_by_visit_model(visit_model)
        else:
            visits = self.visits
        visit = visits.get(code, {})
        previous_visit_list = sorted(
            [(v.time_point, v.code) for v in self.visits.values()
             if v.time_point < visit.time_point], key=lambda x: x[0])
        try:
            previous_visit = previous_visit_list[-1:][0]
        except IndexError:
            previous_visit = None
        if previous_visit:
            previous_visit = self.visits.get(previous_visit[CODE])
        return previous_visit

    @property
    def ordered_visits(self):
        ordered_visits = sorted(self.visits.values(), key=lambda x: x.time_point)
        return [x for x in ordered_visits]

    def relativedelta_from_base(self, visit_code):
        """Returns the relativedelta from the zero time_point visit."""
        visit = self.visits.get(visit_code)
        if visit.base_interval == 0:
            rdelta = relativedelta(days=0)
        else:
            if visit.base_interval_unit == 'Y':
                rdelta = relativedelta(years=visit.base_interval)
            elif visit.base_interval_unit == 'M':
                rdelta = relativedelta(months=visit.base_interval)
            elif visit.base_interval_unit == 'D':
                rdelta = relativedelta(days=visit.base_interval)
            elif visit.base_interval_unit == 'H':
                rdelta = relativedelta(hours=visit.base_interval)
            else:
                raise AttributeError(
                    "Cannot calculate relativedelta, visit.base_interval_unit "
                    "must be Y,M,D or H. Got %s" % (visit.base_interval_unit, ))
        return rdelta
