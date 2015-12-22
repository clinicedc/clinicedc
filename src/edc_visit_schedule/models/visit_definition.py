from datetime import timedelta

from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.db import models

from edc.core.bhp_content_type_map.models import ContentTypeMap

from ..managers import VisitDefinitionManager
from ..models import BaseWindowPeriodItem
from ..models import ScheduleGroup
from ..utils import get_lower_window_days, get_upper_window_days
from ..validators import is_visit_tracking_model


class VisitDefinition(BaseWindowPeriodItem):
    """Model to define a visit code, title, windows, schedule_group, etc."""
    code = models.CharField(
        max_length=6,
        validators=[MaxLengthValidator(6)],
        db_index=True,
        unique=True)
    title = models.CharField(
        verbose_name="Title",
        max_length=35,
        db_index=True)
    visit_tracking_content_type_map = models.ForeignKey(ContentTypeMap,
        null=True,
        verbose_name='Visit Tracking Model',
        validators=[is_visit_tracking_model, ])
    schedule_group = models.ManyToManyField(ScheduleGroup,
        null=True,
        blank=True,
        help_text="Visit definition may be used in more than one schedule_group")
    instruction = models.TextField(
        verbose_name="Instructions",
        max_length=255,
        blank=True)
    objects = VisitDefinitionManager()

    def natural_key(self):
        return (self.code, )

    def get_lower_window_datetime(self, appt_datetime):
        if not appt_datetime:
            return None
        days = get_lower_window_days(self.lower_window, self.lower_window_unit)
        td = timedelta(days=days)
        return appt_datetime - td

    def get_upper_window_datetime(self, appt_datetime):
        if not appt_datetime:
            return None
        days = get_upper_window_days(self.upper_window, self.upper_window_unit)
        td = timedelta(days=days)
        return appt_datetime + td

    def __unicode__(self):
        return '{0}: {1}'.format(self.code, self.title)

    def get_absolute_url(self):
        return reverse('admin:bhp_visit_visitdefinition_change', args=(self.id,))

    class Meta:
        ordering = ['code', 'time_point']
        app_label = "visit_schedule"
        db_table = 'bhp_visit_visitdefinition'
