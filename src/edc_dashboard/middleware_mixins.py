class EdcTemplateMiddlewareMixin:
    def check_for_required_request_attrs(self, request):
        try:
            request.url_name_data  # noqa: B018
        except AttributeError:
            request.url_name_data = {}
        try:
            request.template_data  # noqa: B018
        except AttributeError:
            request.template_data = {}
