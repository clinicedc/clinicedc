from django.urls.base import reverse
from django.conf import settings
from django.utils.safestring import mark_safe


class ModelAdminSubjectDashboardMixin:

    subject_dashboard_url = "subject_dashboard_url"

    def dashboard(self, obj=None):
        url = reverse(
            settings.DASHBOARD_URL_NAMES.get(self.subject_dashboard_url),
            kwargs=dict(subject_identifier=obj.subject_identifier),
        )
        return mark_safe(
            f"<span nowrap>{obj.subject_identifier}&nbsp;"
            f'<a class="button" title="Go to subject\'s dashboard" '
            f'href="{url}">Go</a></span>'
        )

    dashboard.short_description = "Dashboard"
