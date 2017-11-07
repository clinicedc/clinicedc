import re

from .forms_collection import FormsCollection
from .window_period import WindowPeriod


class VisitCodeError(Exception):
    pass


class VisitDateError(Exception):
    pass


class VisitDate:

    window_period_cls = WindowPeriod

    def __init__(self, **kwargs):
        self._base = None
        self._window = self.window_period_cls(**kwargs)
        self.lower = None
        self.upper = None

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, dt=None):
        if not self._base:
            self._base = dt
            window = self._window.get_window(dt=dt)
            self.lower = window.lower
            self.upper = window.upper


class Visit:

    code_regex = r'^([A-Z0-9])+$'
    forms_collection_cls = FormsCollection
    visit_date_cls = VisitDate

    def __init__(self, code=None, timepoint=None, rbase=None, rlower=None,
                 rupper=None, crfs=None, requisitions=None, crfs_unscheduled=None,
                 requisitions_unscheduled=None, title=None,
                 instructions=None, grouping=None, appointment_model=None,
                 allow_unscheduled=None, **kwargs):

        self.appointment_model = appointment_model
        self.dates = self.visit_date_cls(
            rlower=rlower, rupper=rupper, **kwargs)
        self.title = title or f'Visit {code}'
        if not code or isinstance(code, int) or not re.match(self.code_regex, code):
            raise VisitCodeError(f'Invalid visit code. Got \'{code}\'')
        else:
            self.code = code  # unique
        self.name = self.code
        self.crfs = self.forms_collection_cls(*(crfs or []), **kwargs).forms
        self.requisitions = self.forms_collection_cls(
            *(requisitions or []), **kwargs).forms
        self.crfs_unscheduled = crfs_unscheduled
        self.requisitions_unscheduled = requisitions_unscheduled
        self.allow_unscheduled = allow_unscheduled

        self.instructions = instructions
        self.timepoint = timepoint
        self.rbase = rbase
        self.rlower = rlower
        self.rupper = rupper
        self.grouping = grouping

    def __repr__(self):
        return f'Visit({self.code}, {self.timepoint})'

    def __str__(self):
        return self.title

    @property
    def forms(self):
        return self.crfs + self.requisitions

    @property
    def timepoint_datetime(self):
        return self.dates.base

    @timepoint_datetime.setter
    def timepoint_datetime(self, dt=None):
        self.dates.base = dt
