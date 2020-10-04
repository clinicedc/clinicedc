from collections import namedtuple

import arrow


class WindowPeriod:
    def __init__(self, rlower=None, rupper=None, visit_code=None):
        self.rlower = rlower
        self.rupper = rupper

    def get_window(self, dt=None):
        """Returns a named tuple of the lower and upper values.
        """
        dt_floor = arrow.get(dt).to("utc").replace(hour=0, minute=0).datetime
        dt_ceil = arrow.get(dt).to("utc").replace(hour=23, minute=59).datetime
        Window = namedtuple("window", ["lower", "upper"])
        return Window(dt_floor - self.rlower, dt_ceil + self.rupper)
