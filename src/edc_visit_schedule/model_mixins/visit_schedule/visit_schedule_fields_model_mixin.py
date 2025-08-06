from django.db import models


class VisitScheduleFieldsModelMixin(models.Model):
    """A model mixin that adds fields required to work with the visit
    schedule methods on the VisitScheduleMethodsModelMixin.

    Note: visit_code is not included.
    """

    visit_schedule_name = models.CharField(
        max_length=25,
        editable=False,
        help_text='the name of the visit schedule used to find the "schedule"',
    )

    schedule_name = models.CharField(max_length=25, editable=False)

    class Meta:
        abstract = True
