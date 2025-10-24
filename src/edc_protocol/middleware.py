from .research_protocol_config import ResearchProtocolConfig


class ResearchProtocolConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):  # noqa: ARG002
        if getattr(response, "context_data", None):
            protocol_config = ResearchProtocolConfig()
            response.context_data.update(
                copyright=protocol_config.copyright,
                disclaimer=protocol_config.disclaimer,
                institution=protocol_config.institution,
                license=protocol_config.license,
                project_name=protocol_config.project_name,
            )
        return response
