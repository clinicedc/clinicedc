

class Visit:
    """A class that represents a "visit" of schedule.

    Is contained by a "schedule".
    """

    def __init__(
            self, code=None, title=None, timepoint_datetime=None,
            is_scheduled=None,
            ** kwargs):
        self.code = code
        self.title = title or f'Visit {code}'
        self.timepoint_datetime = timepoint_datetime
        self.is_scheduled = is_scheduled

    def __repr__(self):
        return f'Visit({self.code}, {self.title})'

    def __str__(self):
        return self.title
