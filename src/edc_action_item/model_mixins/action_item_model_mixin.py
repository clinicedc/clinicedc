from django.conf import settings
from django.db import models
from django.urls.base import reverse
from django.utils.safestring import mark_safe


class ActionItemModelMixin(models.Model):

    action_cls = None

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    subject_dashboard_url = 'subject_dashboard_url'

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
