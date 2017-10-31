from .timepoint_selector import TimepointSelector
from .visit import Visit


class Schedule:

    """A class that represents a "schedule" of medication plan.
    Is contained by a "schedules".
    """
    timepoint_selector_cls = TimepointSelector

    def __init__(self, period, name=None, number_of_visits=None,
                 description=None):
        self._visits = {}
        self.period = period
        self.name = name
        self.number_of_visits = number_of_visits or 1
        self.workdays = self.period.workdays
        self.description = description
        self.selector = self.timepoint_selector_cls(
            workdays=self.workdays,
            number_of_visits=self.number_of_visits)
        self.prepare()

    def add(self, visit=None):
        self._visits.update({visit.code: visit})

    @property
    def visits(self):
        return self._visits

    def __repr__(self):
        return f'Visit({self.name})'

    def prepare(self):
        for i, timepoint in enumerate(self.selector.selected_timepoints):
            visit = Visit(
                code=f'visit{i}', title=i,
                timepoint_datetime=timepoint)
            self.add(visit)
