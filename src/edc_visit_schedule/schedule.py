from edc_visit_schedule.visit import Visit
from dateutil.relativedelta import relativedelta


class Schedule:
    def __init__(self, name, grouping_key=None):
        self.name = name
        self.visits = {}
        # may specify a common value to group a number of membership forms so '
        # that when one of the group is keyed, the others are no longer shown.'
        self.grouping_key = grouping_key

    def __str__(self):
        return self.name

    @property
    def group_name(self):
        return self.name

    def add_visit(self, code, title, visit_model, schedule, **kwargs):
        visit = Visit(code, title, visit_model, schedule, **kwargs)
        self.visits.update(code=visit)

    def relativedelta_from_base(self, visit_code):
        """Returns the relativedelta from the zero time_point visit."""
        visit = self.visits.get(visit_code)
        if visit.base_interval == 0:
            rdelta = relativedelta(days=0)
        else:
            if visit.base_interval_unit == 'Y':
                rdelta = relativedelta(years=visit.base_interval)
            elif visit.base_interval_unit == 'M':
                rdelta = relativedelta(months=visit.base_interval)
            elif visit.base_interval_unit == 'D':
                rdelta = relativedelta(days=visit.base_interval)
            elif visit.base_interval_unit == 'H':
                rdelta = relativedelta(hours=visit.base_interval)
            else:
                raise AttributeError(
                    "Cannot calculate relativedelta, visit.base_interval_unit "
                    "must be Y,M,D or H. Got %s" % (visit.base_interval_unit, ))
        return rdelta
