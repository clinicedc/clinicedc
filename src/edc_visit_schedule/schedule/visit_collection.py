from collections import OrderedDict
from datetime import datetime
from typing import Any

from ..ordered_collection import OrderedCollection


class VisitCollectionError(Exception):
    pass


class VisitCollection(OrderedCollection):

    key: str = "code"
    ordering_attr: str = "timepoint"

    def __get__(self, instance: Any, owner: Any):
        value = super().__get__(instance, owner)  # type: ignore
        if value is None:
            raise VisitCollectionError(f"Unknown visit. Got {instance}")
        return value

    def timepoint_dates(self, dt: datetime) -> dict:
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
