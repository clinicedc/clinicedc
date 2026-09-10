from __future__ import annotations

from collections import namedtuple
from decimal import Decimal
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from multisite.utils import get_multisite_timezone

from edc_utils.date import to_local

Window = namedtuple("Window", ["lower", "upper"])


class WindowPeriod:
    def __init__(
        self,
        *,
        rlower: relativedelta,
        rupper: relativedelta,
        timepoint: Decimal | None = None,
        base_timepoint: Decimal | None = None,
        no_floor: bool | None = None,
        no_ceil: bool | None = None,
    ):
        self.rlower = rlower
        self.rupper = rupper
        self.no_floor = no_floor
        self.no_ceil = no_ceil
        self.timepoint = Decimal("0.0") if timepoint is None else timepoint
        base_timepoint = Decimal("0.0") if base_timepoint is None else base_timepoint
        if self.timepoint == base_timepoint:
            self.no_floor = True

    def get_window(self, dt=None) -> Window:
        """Returns a tuple of the lower and upper datetimes in local time."""

        dt_floor = (
            to_local(dt)
            if self.no_floor
            else dt.astimezone(ZoneInfo(get_multisite_timezone())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        )
        dt_ceil = (
            to_local(dt)
            if self.no_ceil
            else dt.astimezone(ZoneInfo(get_multisite_timezone())).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        )
        return Window(dt_floor - self.rlower, dt_ceil + self.rupper)
