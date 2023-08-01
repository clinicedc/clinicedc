from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from typing import TYPE_CHECKING

from ..ordered_collection import OrderedCollection

if TYPE_CHECKING:
    from .. import Visit


class VisitCollectionError(Exception):
    pass


class VisitCollection(OrderedCollection):
    key: str = "code"
    ordering_attr: str = "timepoint"

    def get(self, visit_code: str) -> Visit:
        """Return a visit for the given visit_code or raise"""
        value = super().get(visit_code)
        if value is None:
            raise VisitCollectionError(
                f"Unknown visit. Check the visit schedule. Got visit_code={visit_code}"
            )
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

        last_dte = None
        for dte in timepoint_dates.values():
            if not last_dte:
                last_dte = dte
                continue
            if dte and last_dte and not dte > last_dte:
                raise VisitCollectionError(
                    "Wait! timepoint datetimes are not in sequence. "
                    f"Check visit.rbase in your visit collection. See {self}."
                )

        return timepoint_dates

    @property
    def timepoints(self) -> dict:
        timepoints = {}
        for visit in self.values():
            timepoints.update({visit: visit.timepoint})
        return timepoints
