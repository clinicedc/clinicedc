from django.conf import settings
from edc_dashboard import insert_bootstrap_version

from .dashboard_templates import dashboard_templates


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *args) -> None:
        template_data = dashboard_templates
        try:
            template_data.update(settings.REVIEW_DASHBOARD_BASE_TEMPLATES)
        except AttributeError:
            pass
        template_data = insert_bootstrap_version(**template_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.template_data)
        return response
