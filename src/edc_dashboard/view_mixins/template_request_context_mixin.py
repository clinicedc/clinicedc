class TemplateRequestContextError(Exception):
    pass


class TemplateRequestContextMixin:

    """Adds a method to get a specified template from the request.context_data.

    For example:
        def get_template_names(self):
            return [self.get_template_from_context(self.listboard_template)]
    """

    def get_template_from_context(self, key=None):
        """Returns a template_name from request.context_data.
        """
        try:
            template_name = self.request.template_data[key]
        except KeyError as e:
            raise TemplateRequestContextError(
                f'Template name not defined in request context data. '
                f'Expected one of {list(self.request.template_data.keys())}. Got {e}.')
        return template_name
