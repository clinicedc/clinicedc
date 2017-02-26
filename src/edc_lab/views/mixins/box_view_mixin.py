from django.apps import apps as django_apps
from django.contrib import messages
from django.utils.html import escape

from ...exceptions import SpecimenError


class IdentifierDoesNotExist(Exception):
    pass


class BoxViewMixin:

    box_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_model.split('.'))
    box_item_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_item_model.split('.'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._box = None
        self._box_item = None
        self._box_identifier = None
        self._box_item_identifier = None
        self.original_box_item_identifier = None
        self.original_box_identifier = None

    @property
    def box_identifier(self):
        if not self._box_identifier:
            self.original_box_identifier = escape(
                self.kwargs.get('box_identifier')).strip()
            self._box_identifier = ''.join(
                self.original_box_identifier.split('-'))
        return self._box_identifier

    @property
    def box_item_identifier(self):
        """Returns a cleaned box_item_identifier or None.
        """
        if not self._box_item_identifier:
            self.original_box_item_identifier = escape(
                self.request.POST.get('box_item_identifier', '')).strip()
            if self.original_box_item_identifier:
                self._box_item_identifier = self._clean_box_item_identifier()
        return self._box_item_identifier

    @property
    def box(self):
        if not self._box:
            if self.box_identifier:
                try:
                    self._box = self.box_model.objects.get(
                        box_identifier=self.box_identifier)
                except self.box_model.DoesNotExist:
                    self._box = None
        return self._box

    @property
    def box_item(self):
        """Returns a box item model instance.
        """
        if not self._box_item:
            if self.box_item_identifier:
                try:
                    self._box_item = self.box_item_model.objects.get(
                        box=self.box,
                        identifier=self.box_item_identifier)
                except self.box_item_model.DoesNotExist:
                    message = 'Invalid identifier for box. Got {}'.format(
                        self.original_box_item_identifier)
                    messages.error(self.request, message)
        return self._box_item

    def get_box_item(self, position):
        """Returns a box item model instance for the given position.
        """
        try:
            box_item = self.box_item_model.objects.get(
                box=self.box,
                position=position)
        except self.box_item_model.DoesNotExist:
            message = 'Invalid position for box. Got {}'.format(
                position)
            messages.error(self.request, message)
            return None
        return box_item

    def _clean_box_item_identifier(self):
        """Returns a valid identifier or raises.
        """
        aliqout_model = django_apps.get_model(
            *django_apps.get_app_config('edc_lab').aliquot_model.split('.'))
        box_item_identifier = ''.join(
            self.original_box_item_identifier.split('-'))
        try:
            obj = aliqout_model.objects.get(
                aliquot_identifier=box_item_identifier)
        except aliqout_model.DoesNotExist:
            message = 'Invalid aliquot identifier. Got {}.'.format(
                self.original_box_item_identifier or 'None')
            messages.error(self.request, message)
            raise SpecimenError(message)
        if obj.is_primary and not self.box.accept_primary:
            message = 'Box does not accept "primary" specimens. Got {} is primary.'.format(
                self.original_box_item_identifier)
            messages.error(self.request, message)
            raise SpecimenError(message)
        elif obj.aliquot_type not in self.box.specimen_types.split(','):
            message = (
                'Invalid specimen type. Box accepts types {}. '
                'Got {} is type {}.'.format(
                    ', '.join(self.box.specimen_types.split(',')),
                    self.original_box_item_identifier,
                    obj.aliquot_type))
            messages.error(self.request, message)
            raise SpecimenError(message)
        return box_item_identifier

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            box_identifier=self.original_box_identifier,
            box_item_identifier=self.original_box_item_identifier,
            box=self.box)
        return context
