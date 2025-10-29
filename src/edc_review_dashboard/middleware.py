import contextlib

from django.conf import settings

from edc_dashboard.middleware_mixins import EdcTemplateMiddlewareMixin

from .dashboard_templates import dashboard_templates


class DashboardMiddleware(EdcTemplateMiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_for_required_request_attrs(request)
        return self.get_response(request)

    def process_view(self, request, *args) -> None:
        template_data = dashboard_templates
        with contextlib.suppress(AttributeError):
            template_data.update(settings.REVIEW_DASHBOARD_BASE_TEMPLATES)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if getattr(response, "context_data", None):
            response.context_data.update(**request.template_data)
            request.template_data.update(**request.template_data)
        return response
