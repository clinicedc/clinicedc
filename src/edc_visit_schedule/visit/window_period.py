from __future__ import annotations

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.conf import settings

from edc_utils import to_local


class WindowPeriod:
    def __init__(
        self,
        rlower: relativedelta = None,
        rupper: relativedelta = None,
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

    def get_window(self, dt=None) -> tuple[datetime, datetime]:
        """Returns a tuple of the lower and upper datetimes in local time."""

        dt_floor = (
            to_local(dt)
            if self.no_floor
            else dt.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(
                ZoneInfo(settings.TIME_ZONE)
            )
        )
        dt_ceil = (
            to_local(dt)
            if self.no_ceil
            else dt.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(
                ZoneInfo(settings.TIME_ZONE)
            )
        )
        window = namedtuple("Window", ["lower", "upper"])
        return window(dt_floor - self.rlower, dt_ceil + self.rupper)
