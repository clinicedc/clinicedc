from django.db import models


class ScheduleGroupManager(models.Manager):

    def get_by_natural_key(self, group_name):
        return self.get(group_name=group_name)
