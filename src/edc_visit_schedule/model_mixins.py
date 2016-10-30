from django.db import models
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class VisitScheduleModelMixin(models.Model):

    """Adds field attributes that link a model instance to the schedule.

    Fields must be updated manually. For example, appointment updates these fields
    when created.

    See also CreateAppointmentsMixin. """

    visit_schedule_name = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text='the name of the visit schedule used to find the "schedule"')

    schedule_name = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text='the name of the schedule used to find the list of "visits" to create appointments')

    visit_code = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    @property
    def schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        return visit_schedule.get_schedule(self.schedule_name)

    class Meta:
        abstract = True
