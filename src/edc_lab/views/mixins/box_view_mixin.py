from django.apps import apps as django_apps
from django.contrib import messages

from ...exceptions import SpecimenError
from .container_view_mixin import ContainerViewMixin


class IdentifierDoesNotExist(Exception):
    pass


class BoxViewMixin(ContainerViewMixin):

    container_name = 'box'
    container_item_name = 'box_item'
    container_identifier_name = 'box_identifier'
    item_model_identifier_name = 'identifier'
    item_request_identifier_name = 'box_item_identifier'
    container_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_model.split('.'))
    container_item_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_item_model.split('.'))

    @property
    def box_model(self):
        return self.container_model

    @property
    def box_item_model(self):
        return self.container_item_model

    @property
    def box(self):
        return self.container

    @property
    def box_identifier(self):
        return self.container_identifier

    @property
    def box_item(self):
        return self.container_item

    @property
    def box_item_identifier(self):
        return self.container_item_identifier

    def get_box_item(self, position):
        return self.get_container_item(position)

    def _clean_container_item_identifier(self):
        """Returns a valid identifier or raises.
        """
        aliqout_model = django_apps.get_model(
            *django_apps.get_app_config('edc_lab').aliquot_model.split('.'))
        container_item_identifier = ''.join(
            self.original_container_item_identifier.split('-'))
        try:
            obj = aliqout_model.objects.get(
                aliquot_identifier=container_item_identifier)
        except aliqout_model.DoesNotExist:
            message = 'Invalid aliquot identifier. Got {}.'.format(
                self.original_container_item_identifier or 'None')
            messages.error(self.request, message)
            raise SpecimenError(message)
        if obj.is_primary and not self.container.accept_primary:
            message = 'Box does not accept "primary" specimens. Got {} is primary.'.format(
                self.original_container_item_identifier)
            messages.error(self.request, message)
            raise SpecimenError(message)
        elif obj.aliquot_type not in self.container.specimen_types.split(','):
            message = (
                'Invalid specimen type. Box accepts types {}. '
                'Got {} is type {}.'.format(
                    ', '.join(self.container.specimen_types.split(',')),
                    self.original_container_item_identifier,
                    obj.aliquot_type))
            messages.error(self.request, message)
            raise SpecimenError(message)
        return container_item_identifier
