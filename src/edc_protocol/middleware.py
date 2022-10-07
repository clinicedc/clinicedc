from .protocol import Protocol


class ProtocolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *args):
        pass

    def process_template_response(self, request, response):
        if not response.context_data:
            response.context_data = {}
        protocol = Protocol()
        response.context_data.update(
            copyright=protocol.copyright,
            disclaimer=protocol.disclaimer,
            institution=protocol.institution,
            license=protocol.license,
            project_name=protocol.project_name,
        )
        return response
