from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from ..models import ActionItem


class ActionClassNotDefined(Exception):
    pass


class ActionItemModelMixin(models.Model):

    action_cls = None
    subject_dashboard_url = 'subject_dashboard_url'

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    def save(self, *args, **kwargs):
        if not self.action_cls:
            raise ActionClassNotDefined(
                f'Action class not defined. See {repr(self)}')
        super().save(*args, **kwargs)

    @property
    def action_item(self):
        try:
            return ActionItem.objects.get(action_identifier=self.action_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def action_item_reason(self):
        return None

    class Meta:
        abstract = True
