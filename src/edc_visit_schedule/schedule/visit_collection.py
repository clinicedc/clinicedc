from collections import OrderedDict

from ..ordered_collection import OrderedCollection


class VisitCollection(OrderedCollection):

    key = 'code'
    ordering_attr = 'timepoint'

    def timepoint_dates(self, dt=None):
        """Returns an ordered dictionary of visit dates calculated
        relative to the first visit."""
        timepoint_dates = OrderedDict()
        for visit in self.values():
            visit.timepoint_datetime = dt + visit.rbase
            timepoint_dates.update({visit: visit.timepoint_datetime})
        return timepoint_dates
