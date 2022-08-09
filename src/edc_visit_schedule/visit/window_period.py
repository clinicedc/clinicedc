from collections import namedtuple
from zoneinfo import ZoneInfo


class WindowPeriod:
    def __init__(self, rlower=None, rupper=None, visit_code=None):
        self.rlower = rlower
        self.rupper = rupper

    def get_window(self, dt=None):
        """Returns a named tuple of the lower and upper values."""
        dt_floor = dt.astimezone(ZoneInfo("UTC")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        dt_ceil = dt.astimezone(ZoneInfo("UTC")).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        Window = namedtuple("window", ["lower", "upper"])
        return Window(dt_floor - self.rlower, dt_ceil + self.rupper)
