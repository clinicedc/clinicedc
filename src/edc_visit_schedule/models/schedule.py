from django.db import models

from edc_base.model.models import BaseUuidModel

from ..models import MembershipForm


class ScheduleManager(models.Manager):

    def get_by_natural_key(self, group_name):
        return self.get(group_name=group_name)


class Schedule(BaseUuidModel):
    """Model that groups membership forms"""

    group_name = models.CharField(
        max_length=25,
        unique=True)

    membership_form = models.ForeignKey(MembershipForm)

    grouping_key = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text=(
            'may specify a common value to group a number of membership forms so '
            'that when one of the group is keyed, the others are no longer shown.'))

    comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = ScheduleManager()

    def natural_key(self):
        return (self.group_name, )

    def __unicode__(self):
        return unicode(self.group_name)

    class Meta:
        ordering = ['group_name']
        app_label = "edc_visit_schedule"
