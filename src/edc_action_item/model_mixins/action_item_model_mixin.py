from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from ..models import ActionType, ActionItem


class InvalidActionType(Exception):
    pass


class ActionItemModelMixin(models.Model):

    action_identifier = models.CharField(
        max_length=25,
        unique=True)

    def action_item_rules(self):
        """Conditional statements that if True call
        `create_or_update_action_item`.
        """
        pass

    def create_or_update_action_item(self, action_item_name, **kwargs):
        try:
            action_type = ActionType.objects.get(name=action_item_name)
        except ObjectDoesNotExist:
            raise InvalidActionType(
                f'Invalid action type. Got action_type.name=\'{action_item_name}\'.')
        try:
            action_item = ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                action_type=action_type,
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist:
            action_item = ActionItem.objects.create(
                subject_identifier=self.subject_identifier,
                action_type=action_type)
        else:
            action_item
        self.action_identifier = action_item.action_identifier

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url"),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    class Meta:
        abstract = True
