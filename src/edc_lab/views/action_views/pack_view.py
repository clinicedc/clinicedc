from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.utils.decorators import method_decorator

from ...models import Manifest, ManifestItem
from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView, app_config
from edc_lab.constants import SHIPPED


class PackView(BoxViewMixin, BaseActionView):

    post_url_name = app_config.pack_listboard_url_name
    box_item_failed = False
    valid_form_actions = [
        'add_selected_to_manifest', 'remove_selected_items']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_manifest = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'remove_selected_items':
            self.remove_selected_items()
        elif self.action == 'add_selected_to_manifest':
            if self.selected_manifest:
                self.add_selected_to_manifest()

    @property
    def selected_manifest(self):
        if not self._selected_manifest:
            try:
                self._selected_manifest = Manifest.objects.get(
                    pk=self.request.POST.get('selected_manifest'))
            except Manifest.DoesNotExist:
                pass
        return self._selected_manifest

    def add_selected_to_manifest(self):
        """Adds the selected items to the selected manifest.
        """
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                for selected_item in self.selected_items:
                    box = self.box_model.objects.get(pk=selected_item)
                    ManifestItem.objects.create(
                        identifier=box.box_identifier,
                        manifest=self.selected_manifest)
                    box.status = SHIPPED
                    box.save()
                message = (
                    '{} items have been added to manifest {}.'.format(
                        len(self.selected_items),
                        self.selected_manifest.human_readable_identifier))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Box is not empty.')
                messages.error(self.request, message)

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.manifest_item.objects.filter(
                    pk__in=self.selected_items).delete()
                message = ('{} items have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Box is not empty.')
                messages.error(self.request, message)
