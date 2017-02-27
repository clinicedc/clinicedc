from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from ...exceptions import BoxItemError
from ..mixins import ManifestViewMixin
from .base_action_view import BaseActionView, app_config
from edc_lab.models.manifest_item import ManifestItem
from edc_lab.models.box import Box
from edc_lab.constants import VERIFIED


class ManageManifestView(ManifestViewMixin, BaseActionView):

    post_url_name = app_config.manage_manifest_listboard_url_name
    valid_form_actions = [
        'add_item', 'remove_selected_items']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.kwargs.get('action_name'),
            'manifest_identifier': self.manifest_identifier}

    @property
    def box(self):
        try:
            return Box.objects.get(box_identifier=self.manifest_item_identifier)
        except Box.DoesNotExist:
            return None

    def process_form_action(self):
        if self.action == 'add_item':
            try:
                if self.manifest_item_identifier:
                    self.add_item()
            except BoxItemError:
                pass
        elif self.action == 'remove_selected_items':
            self.remove_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.manifest_item_model.objects.filter(
                    pk__in=self.selected_items).delete()
                message = ('{} items have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Manifest is not empty.')
                messages.error(self.request, message)

    def add_item(self, **kwargs):
        """Adds the item to the manifest.
        """
        if self.box and self.box.status != VERIFIED:
            message = 'Box is not verified. Got {}.'.format(
                self.box.box_identifier)
            messages.error(self.request, message)
        elif not self.box:
            message = 'Box does not exist. Got {}.'.format(
                self.manifest_item_identifier)
            messages.error(self.request, message)
        else:
            try:
                manifest_item = self.manifest_item_model.objects.get(
                    manifest__manifest_identifier=self.manifest_identifier,
                    identifier=self.manifest_item_identifier)
            except self.manifest_item_model.DoesNotExist:
                try:
                    manifest_item = self.manifest_item_model.objects.get(
                        identifier=self.manifest_item_identifier)
                except self.manifest_item_model.DoesNotExist:
                    manifest_item = self.manifest_item_model(
                        manifest=self.manifest,
                        identifier=self.manifest_item_identifier)
                    manifest_item.save()
                else:
                    message = mark_safe(
                        'Item is already in a manifest. See <a href="{href}" class="alert-link">'
                        '{manifest_identifier}</a>'.format(
                            href=reverse(
                                self.listboard_url_name,
                                kwargs={
                                    'manifest_identifier':
                                    manifest_item.manifest.manifest_identifier}),
                            manifest_identifier=manifest_item.manifest.manifest_identifier))
                    messages.error(self.request, message)
            else:
                message = 'Duplicate item. Got {}.'.format(
                    manifest_item.manifest.manifest_identifier)
                messages.error(self.request, message)
