from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView, app_config


class ManifestView(BoxViewMixin, BaseActionView):

    post_url_name = app_config.manage_box_listboard_url_name
    valid_form_actions = [
        'add_item', 'remove_selected_items']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {'manifest_identifier': self.manifest_identifier}

    def process_form_action(self):
        if self.action == 'add_item':
            self.add_box()
        elif self.action == 'remove_selected_items':
            self.remove_selected_items()

    def remove_selected_items(self):
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.box_model.objects.filter(
                    pk__in=self.selected_items).delete()
                message = ('{} items have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Manifest is not empty.')
                messages.error(self.request, message)

    def add_item(self, **kwargs):
        """Adds the item to the next available position in the manifest.
        """
        try:
            manifest_item = self.manifest_item.objects.get(
                manifest__manifest_identifier=self.manifest_identifier,
                identifier=self.manifest_item_identifier)
        except self.manifest_item.DoesNotExist:
            try:
                manifest_item = self.manifest_item.objects.get(
                    identifier=self.manifest_item_identifier)
            except self.manifest_item.DoesNotExist:
                manifest_item = self.manifest_item(
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
                manifest_item.manifest_identifier)
            messages.error(self.request, message)
