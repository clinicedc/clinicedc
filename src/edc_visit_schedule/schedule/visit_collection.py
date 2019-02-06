from collections import OrderedDict

from ..ordered_collection import OrderedCollection


class VisitCollectionError(Exception):
    pass


class VisitCollection(OrderedCollection):

    key = "code"
    ordering_attr = "timepoint"

    def timepoint_dates(self, dt=None):
        """Returns an ordered dictionary of visit dates calculated
        relative to the first visit.
        """
        timepoint_dates = OrderedDict()
        for visit in self.values():
            try:
                timepoint_datetime = dt + visit.rbase
            except TypeError as e:
                raise VisitCollectionError(
                    f"Invalid visit.rbase. visit.rbase={visit.rbase}. "
                    f"See {repr(visit)}. Got {e}."
                )
            else:
                visit.timepoint_datetime = timepoint_datetime
            timepoint_dates.update({visit: visit.timepoint_datetime})
        return timepoint_dates
