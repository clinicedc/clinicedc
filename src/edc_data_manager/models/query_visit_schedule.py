from edc_visit_schedule.models import VisitSchedule


class QueryVisitSchedule(VisitSchedule):

    class Meta:
        proxy = True
        default_permissions = ("view", )
        verbose_name = "Visit Schedule"
        verbose_name_plural = "Visit Schedule"
