from edc_visit_schedule.visit import Visit
from dateutil.relativedelta import relativedelta
from edc_visit_schedule.exceptions import AlreadyRegistered, ScheduleError, CrfError


class Schedule:
    def __init__(self, name, enrollment_model, off_study_model=None, death_report_model=None,
                 grouping_key=None):
        self.visit_model = None
        self.name = name
        self.visit_registry = {}
        self.enrollment_model = enrollment_model
        try:
            enrollment_model.create_appointments
        except AttributeError as e:
            raise ScheduleError('Enrollment model not configured to create appointments. Got {}'.format(str(e)))
        self.off_study_model = off_study_model
        self.death_report_model = death_report_model

    def __str__(self):
        return self.name

    def add_visit(self, code, **kwargs):
        visit = Visit(code, **kwargs)
        if visit.code in self.visit_registry:
            raise AlreadyRegistered(
                'Visit is already registered with schedule \'{}\'. Got {}'.format(self.name, visit))
        if visit.timepoint in [v.timepoint for v in self.visit_registry.values()]:
            raise ScheduleError(
                'Visit with timepoint \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.timepoint, self.name, visit))
        if visit.base_interval in [v.base_interval for v in self.visit_registry.values()]:
            raise ScheduleError(
                'Visit with base_interval \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.base_interval, self.name, visit))
        if kwargs.get('crfs'):
            show_orders = sorted([crf.show_order for crf in kwargs.get('crfs')])
            if len(list(set(show_orders))) != len(show_orders):
                raise CrfError(
                    'Crf show order must be a unique sequence. Got {} in schedule {}'.format(show_orders, self.name))
        self.visit_registry.update({code: visit})
        return visit

    def get_visit(self, code, interval=None):
        visit = self.visit_registry.get(code)
        if interval:
            if interval > 0:
                visits = [v for v in self.visits if v.timepoint > visit.timepoint]
            else:
                visits = [i for i in reversed([v for v in self.visits if v.timepoint < visit.timepoint])]
            try:
                visit = visits[abs(interval) - 1]
            except IndexError:
                visit = None
        return visit

    def get_previous_visit(self, code):
        """Returns the previous visit or None."""
        return self.get_visit(code, -1)

    def get_next_visit(self, code):
        """Returns the previous visit or None."""
        return self.get_visit(code, 1)

    @property
    def visits(self):
        ordered_visits = sorted(self.visit_registry.values(), key=lambda x: x.timepoint)
        return [x for x in ordered_visits]

    def relativedelta_from_base(self, code=None):
        """Returns the relativedelta from the zero timepoint visit."""
        visit = self.visit_registry.get(code)
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
