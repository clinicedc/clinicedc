from django.contrib import messages
from django.utils.html import escape


class ContainerViewMixin:

    container_name = None
    container_item_name = None
    container_identifier_name = None
    container_item_identifier_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._container = None
        self._container_item = None
        self._container_identifier = None
        self._container_item_identifier = None
        self.original_container_item_identifier = None
        self.original_container_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            self.container_identifier_name: self.original_container_identifier,
            self.container_item_identifier_name: self.original_container_item_identifier,
            self.container_name: self.container
        })
        return context

    @property
    def container_identifier(self):
        if not self._container_identifier:
            self.original_container_identifier = escape(
                self.kwargs.get(self.container_identifier_name)).strip()
            self._container_identifier = ''.join(
                self.original_container_identifier.split('-'))
        return self._container_identifier

    @property
    def container_item_identifier(self):
        """Returns a cleaned container_item_identifier or None.
        """
        if not self._container_item_identifier:
            self.original_container_item_identifier = escape(
                self.request.POST.get(self.container_item_identifier_name, '')).strip()
            if self.original_container_item_identifier:
                self._container_item_identifier = self._clean_container_item_identifier()
        return self._container_item_identifier

    @property
    def container(self):
        if not self._container:
            if self.container_identifier:
                try:
                    self._container = self.container_model.objects.get(
                        **{self.container_identifier_name: self.container_identifier})
                except self.container_model.DoesNotExist:
                    self._container = None
        return self._container

    @property
    def container_item(self):
        """Returns a container item model instance.
        """
        if not self._container_item:
            if self.container_item_identifier:
                try:
                    self._container_item = self.container_item_model.objects.get(
                        **{self.container_name: self.container,
                           self.container_item_identifier_name: self.container_item_identifier})
                except self.container_item_model.DoesNotExist:
                    message = 'Invalid identifier for container. Got {}'.format(
                        self.original_container_item_identifier)
                    messages.error(self.request, message)
        return self._container_item

    def get_container_item(self, position):
        """Returns a container item model instance for the given position.
        """
        try:
            container_item = self.container_item_model.objects.get(
                **{self.container_name: self.container,
                   'position': position})
        except self.container_item_model.DoesNotExist:
            message = 'Invalid position for container. Got {}'.format(
                position)
            messages.error(self.request, message)
            return None
        return container_item

    def _clean_container_item_identifier(self):
        return self.original_container_item_identifier
