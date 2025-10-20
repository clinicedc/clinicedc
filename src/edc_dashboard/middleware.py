from django.conf import settings

from .dashboard_templates import dashboard_templates
from .url_names import url_names


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *args):
        """Adds/Updates references to urls and templates."""

        try:
            request.url_name_data  # noqa: B018
        except AttributeError:
            request.url_name_data = {}
        request.url_name_data.update(**url_names.registry)

        try:
            request.template_data  # noqa: B018
        except AttributeError:
            request.template_data = {}
        template_data = getattr(settings, "DASHBOARD_BASE_TEMPLATES", {})
        template_data.update(**dashboard_templates)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
