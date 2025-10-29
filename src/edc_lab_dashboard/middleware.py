from django.conf import settings

from edc_dashboard.middleware_mixins import EdcTemplateMiddlewareMixin
from edc_lab.constants import SHIPPED

from .dashboard_templates import dashboard_templates
from .dashboard_urls import dashboard_urls


class DashboardMiddleware(EdcTemplateMiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_for_required_request_attrs(request)
        return self.get_response(request)

    def process_view(self, request, *args):
        lab_dashboard_urls = getattr(settings, "LAB_DASHBOARD_URL_NAMES", {})
        dashboard_urls.update(**lab_dashboard_urls)
        request.url_name_data.update(**dashboard_urls)

        template_data = getattr(settings, "LAB_DASHBOARD_BASE_TEMPLATES", {})
        template_data.update(**dashboard_templates)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if getattr(response, "context_data", None):
            response.context_data.update(SHIPPED=SHIPPED)
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
