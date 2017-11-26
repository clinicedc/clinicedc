from django.views.generic.base import ContextMixin


class UrlRequestContextError(Exception):
    pass


class UrlRequestContextMixin(ContextMixin):

    def add_url_to_context(self, new_key=None, existing_key=None, context=None):
        """Add a url as new_key to the context using the value
        of the existing_key from request.context_data.
        """
        try:
            self.request.url_name_data[existing_key]
        except KeyError as e:
            raise UrlRequestContextError(
                f'Url name not defined in context. '
                f'Expected one of {list(self.request.url_name_data.keys())}. Got {e}.')
        context.update(
            {new_key: self.request.url_name_data.get(existing_key)})
        return context
