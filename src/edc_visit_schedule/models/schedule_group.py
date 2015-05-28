from django.db import models
from django.core.urlresolvers import reverse

from edc_base.model.models import BaseUuidModel

from ..managers import ScheduleGroupManager

from .member import Member


class ScheduleGroup(BaseUuidModel):
    """Model that groups membership forms"""
    group_name = models.CharField(
        max_length=25,
        unique=True
    )

    member = models.ForeignKey(Member)

    grouping_key = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text=(
            'may specify a common value to group a number of member models so '
            'that when one of the group is keyed, the others are no longer shown.')
    )

    comment = models.CharField(
        max_length=25,
        null=True,
        blank=True
    )

    objects = ScheduleGroupManager()

    def natural_key(self):
        return (self.group_name, )

    def __str__(self):
        return str(self.group_name)

    def get_absolute_url(self):
        return reverse('admin:bhp_visit_schedulegroup_change', args=(self.id,))

    class Meta:
        ordering = ['group_name']
        app_label = "edc_visit_schedule"
