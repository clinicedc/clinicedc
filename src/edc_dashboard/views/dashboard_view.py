from django.views.generic.base import TemplateView

from ..view_mixins import UrlRequestContextMixin, TemplateRequestContextMixin


class DashboardView(UrlRequestContextMixin, TemplateRequestContextMixin, TemplateView):

    dashboard_url = None
    dashboard_template = None

    def get_template_names(self):
        return [self.get_template_from_context(self.dashboard_template)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_url_to_context(
            new_key='dashboard_url_name',
            existing_key=self.dashboard_url,
            context=context)
        return context
