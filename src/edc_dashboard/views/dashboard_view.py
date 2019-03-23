from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView

from ..view_mixins import UrlRequestContextMixin, TemplateRequestContextMixin


class DashboardView(UrlRequestContextMixin, TemplateRequestContextMixin, TemplateView):

    dashboard_url = None
    dashboard_template = None

    def __init__(self, **kwargs):
        if not self.dashboard_url:
            raise ImproperlyConfigured(
                f"'dashboard_url' cannot be None. See {repr(self)}."
            )
        if not self.dashboard_template:
            raise ImproperlyConfigured(
                f"'dashboard_template' cannot be None. See {repr(self)}."
            )
        super().__init__(**kwargs)

    def get_template_names(self):
        return [self.get_template_from_context(self.dashboard_template)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_url_to_context(
            new_key="dashboard_url_name",
            existing_key=self.dashboard_url,
            context=context,
        )
        return context
