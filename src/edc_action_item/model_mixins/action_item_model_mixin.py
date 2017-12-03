from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db import models


class InvalidActionType(Exception):
    pass


class ActionItemModelMixin(models.Model):

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    def creates_action_items(self):
        """Returns a list of actions, as action_type names,  to create action items
        once on post_save.
        """
        return []

    def create_next_action_items(self, action_type_name):
        """Returns a list of actions, as action_type names, to be created
        again by this model if the first has been closed on post_save.
        """
        if action_type_name:
            return [action_type_name]
        return []

    def close_action_item_on_save(self):
        """Returns True if action item for \'action_identifier\'
        is to be closed on post_save.
        """
        return True

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url"),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    class Meta:
        abstract = True
