from edc_dashboard.middleware_mixins import EdcTemplateMiddlewareMixin

from .dashboard_templates import dashboard_templates
from .dashboard_urls import dashboard_urls


class DashboardMiddleware(EdcTemplateMiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_for_required_request_attrs(request)
        return self.get_response(request)

    def process_view(self, request, *args):
        request.url_name_data.update(**dashboard_urls)
        request.template_data.update(**dashboard_templates)

    def process_template_response(self, request, response):
        if getattr(response, "context_data", None):
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
