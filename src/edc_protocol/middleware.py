from .trial_settings import trial_settings


class ResearchProtocolConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):  # noqa: ARG002
        if getattr(response, "context_data", None):
            response.context_data.update(
                copyright=trial_settings.copyright,
                disclaimer=trial_settings.disclaimer,
                institution=trial_settings.institution,
                license=trial_settings.license,
                project_name=trial_settings.project_name,
            )
        return response
