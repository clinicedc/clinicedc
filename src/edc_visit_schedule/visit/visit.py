import re

from .forms_collection import FormsCollection
from .window_period import WindowPeriod


class VisitCodeError(Exception):
    pass


class VisitDateError(Exception):
    pass


class Visit:

    code_regex = r'^([A-Z0-9])+$'
    window_period_cls = WindowPeriod
    forms_collection_cls = FormsCollection

    def __init__(self, code=None, timepoint=None, rbase=None,
                 crfs=None, requisitions=None, title=None,
                 instructions=None, grouping=None, base_date=None, **kwargs):

        self.base_date = base_date
        self.title = title or f'Visit {code}'
        self._window = self.window_period_cls(**kwargs).window
        if not code or isinstance(code, int) or not re.match(self.code_regex, code):
            raise VisitCodeError(f'Invalid visit code. Got \'{code}\'')
        else:
            self.code = code  # unique
        self.crfs = self.forms_collection_cls(*(crfs or []), **kwargs).items
        self.requisitions = self.forms_collection_cls(
            *(requisitions or []), **kwargs).items

        self.instructions = instructions
        self.timepoint = timepoint
        self.rbase = rbase

        self.grouping = grouping

    def __repr__(self):
        return f'Visit({self.code}, {self.timepoint})'

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.code

    @property
    def lower_date(self):
        """Returns the datetime of the lower bound
        of the window period.
        """
        try:
            return self._window(dt=self.base_date).lower
        except TypeError as e:
            raise VisitDateError(e) from e

    @property
    def upper_date(self):
        """Returns the datetime of the upper bound
        of the window period.
        """
        try:
            return self._window(dt=self.base_date).upper
        except TypeError as e:
            raise VisitDateError(e) from e
