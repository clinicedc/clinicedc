
class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.url_name_data
        except AttributeError:
            request.url_name_data = {}
        try:
            request.template_data
        except AttributeError:
            request.template_data = {}
        response = self.get_response(request)
        return response
