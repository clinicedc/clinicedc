from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView

from ..url_names import url_names
from ..view_mixins import TemplateRequestContextMixin, UrlRequestContextMixin


class DashboardView(UrlRequestContextMixin, TemplateRequestContextMixin, TemplateView):
    dashboard_url_name = None  # see url_names dictionary
    dashboard_template = None  # may be None if `dashboard_template_name` is defined
    dashboard_template_name = None  # may be None if `dashboard_template` is defined

    urlconfig_getattr = "dashboard_urls"

    def __init__(self, **kwargs):
        if not self.dashboard_template and not self.dashboard_template_name:
            raise ImproperlyConfigured(
                f"Both 'dashboard_template' and 'dashboard_template_name' "
                f"cannot be None. See {self!r}."
            )
        super().__init__(**kwargs)

    @classmethod
    def get_urlname(cls):
        return cls.dashboard_url_name

    @property
    def dashboard_url(self):
        return url_names.get(self.dashboard_url_name)

    def get_template_names(self):
        if self.dashboard_template:
            return [self.dashboard_template]
        return [self.get_template_from_context(self.dashboard_template_name)]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(**{self.dashboard_url_name: url_names.get(self.dashboard_url_name)})
        return super().get_context_data(**kwargs)
