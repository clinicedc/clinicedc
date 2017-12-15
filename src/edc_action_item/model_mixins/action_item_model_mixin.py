from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from ..models import ActionItem


class ActionClassNotDefined(Exception):
    pass


class ActionItemModelMixin(models.Model):

    action_cls = None

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    subject_dashboard_url = 'subject_dashboard_url'

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

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get(self.subject_dashboard_url),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    class Meta:
        abstract = True
