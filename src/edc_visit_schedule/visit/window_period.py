from collections import namedtuple
from zoneinfo import ZoneInfo


class WindowPeriod:
    def __init__(
        self,
        rlower=None,
        rupper=None,
        timepoint=None,
        base_timepoint=None,
        no_floor=None,
        no_ceil=None,
    ):
        self.rlower = rlower
        self.rupper = rupper
        self.no_floor = no_floor
        self.no_ceil = no_ceil
        self.timepoint = 0 if timepoint is None else timepoint
        base_timepoint = 0 if base_timepoint is None else base_timepoint
        if self.timepoint == base_timepoint:
            self.no_floor = True

    def get_window(self, dt=None):
        """Returns a named tuple of the lower and upper values."""
        dt_floor = (
            dt
            if self.no_floor
            else dt.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(
                ZoneInfo("UTC")
            )
        )
        dt_ceil = (
            dt
            if self.no_ceil
            else dt.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(
                ZoneInfo("UTC")
            )
        )
        Window = namedtuple("window", ["lower", "upper"])
        return Window(dt_floor - self.rlower, dt_ceil + self.rupper)
