from collections import namedtuple


class WindowPeriod:
    def __init__(self, rlower=None, rupper=None, **kwargs):
        self.rlower = rlower
        self.rupper = rupper

    def get_window(self, dt=None):
        """Returns a named tuple of the lower and upper values.
        """
        Window = namedtuple("window", ["lower", "upper"])
        return Window(dt - self.rlower, dt + self.rupper)
