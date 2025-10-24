from django.conf import settings

from .dashboard_templates import dashboard_templates
from .middleware_mixins import EdcTemplateMiddlewareMixin
from .url_names import url_names


class DashboardMiddleware(EdcTemplateMiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_for_required_request_attrs(request)
        return self.get_response(request)

    def process_view(self, request, *args):
        """Adds/Updates references to urls and templates."""
        request.url_name_data.update(**url_names.registry)
        template_data = getattr(settings, "DASHBOARD_BASE_TEMPLATES", {})
        template_data.update(**dashboard_templates)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if getattr(response, "context_data", None):
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
