from django.conf import settings


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, *args):
        try:
            url_name_data = settings.DASHBOARD_URL_NAMES
        except AttributeError:
            url_name_data = {}
        try:
            template_data = settings.DASHBOARD_BASE_TEMPLATES
        except AttributeError:
            template_data = {}
        request.url_name_data.update(**url_name_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        response.context_data.update(**request.url_name_data)
        response.context_data.update(**request.template_data)
        return response
