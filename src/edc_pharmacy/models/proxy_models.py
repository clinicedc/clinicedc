from edc_visit_schedule.models import VisitSchedule as BaseVisitSchedule


class VisitSchedule(BaseVisitSchedule):
    class Meta:
        proxy = True
