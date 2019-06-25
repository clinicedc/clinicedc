from django.db import models
from edc_action_item.models import ActionItem as BaseActionItem

from ..action_items import DATA_QUERY_ACTION


class Manager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(action_type__name__in=[DATA_QUERY_ACTION])


class DataManagerActionItem(BaseActionItem):

    objects = Manager()

    class Meta:
        proxy = True
        default_permissions = ("view",)
