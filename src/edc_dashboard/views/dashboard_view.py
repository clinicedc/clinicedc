from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView

from ..view_mixins import UrlRequestContextMixin, TemplateRequestContextMixin


class DashboardView(UrlRequestContextMixin, TemplateRequestContextMixin, TemplateView):

    dashboard_url = None
    dashboard_template = None  # may be None if `dashboard_template_name` is defined
    dashboard_template_name = None  # may be None if `dashboard_template` is defined

    urlconfig_getattr = "dashboard_urls"

    def __init__(self, **kwargs):
        if not self.dashboard_url:
            raise ImproperlyConfigured(
                f"'dashboard_url' cannot be None. See {repr(self)}."
            )
        if not self.dashboard_template and not self.dashboard_template_name:
            raise ImproperlyConfigured(
                f"Both 'dashboard_template' and 'dashboard_template_name' "
                f"cannot be None. See {repr(self)}."
            )
        super().__init__(**kwargs)

    def get_template_names(self):
        if self.dashboard_template_name:
            return [self.dashboard_template_name]
        return [self.get_template_from_context(self.dashboard_template)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_url_to_context(
            new_key="dashboard_url_name",
            existing_key=self.dashboard_url,
            context=context,
        )
        return context
