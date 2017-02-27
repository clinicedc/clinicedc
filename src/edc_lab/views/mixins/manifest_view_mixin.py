from django.apps import apps as django_apps
from django.contrib import messages

from ...exceptions import BoxItemError

from .container_view_mixin import ContainerViewMixin


class ManifestViewMixin(ContainerViewMixin):

    container_name = 'manifest'
    container_item_name = 'manifest_item'
    container_identifier_name = 'manifest_identifier'
    container_item_identifier_name = 'manifest_item_identifier'
    container_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').manifest_model.split('.'))
    container_item_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').manifest_item_model.split('.'))

    @property
    def manifest_model(self):
        return self.container_model

    @property
    def manifest_item_model(self):
        return self.container_item_model

    @property
    def manifest(self):
        return self.container

    @property
    def manifest_identifier(self):
        return self.container_identifier

    @property
    def manifest_item(self):
        return self.container_item

    @property
    def manifest_item_identifier(self):
        return self.container_item_identifier

    def get_manifest_item(self):
        return self.get_container_item()

    def _clean_container_item_identifier(self):
        """Returns a valid identifier or raises.
        """
        box_model = django_apps.get_model(
            *django_apps.get_app_config('edc_lab').box_model.split('.'))
        container_item_identifier = ''.join(
            self.original_container_item_identifier.split('-'))
        try:
            box_model.objects.get(
                box_identifier=container_item_identifier)
        except box_model.DoesNotExist:
            message = 'Invalid box identifier. Got {}.'.format(
                self.original_container_item_identifier or 'None')
            messages.error(self.request, message)
            raise BoxItemError(message)
        return container_item_identifier
