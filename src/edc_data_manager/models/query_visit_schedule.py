from edc_visit_schedule.models import VisitSchedule


class QueryVisitSchedule(VisitSchedule):
    def __str__(self):
        return f"{self.visit_code}: {self.visit_title}"

    class Meta:
        proxy = True
        default_permissions = ("view", "export")
        verbose_name = "Visit Schedule"
        verbose_name_plural = "Visit Schedule"
