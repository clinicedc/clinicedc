from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab.constants import SHIPPED
from edc_lab.labels import ManifestLabel

from ...view_mixins import ManifestViewMixin, ModelsViewMixin
from .action_view import ActionView


class ManifestView(EdcBaseViewMixin, ModelsViewMixin, ManifestViewMixin,
                   ActionView, TemplateView):

    post_action_url = 'manifest_listboard_url'
    valid_form_actions = [
        'remove_selected_items', 'print_labels', 'ship_selected_items']
    label_cls = ManifestLabel

    def process_form_action(self, request=None):
        if self.action == 'remove_selected_items':
            self.remove_selected_items()
        elif self.action == 'print_labels':
            self.print_labels(pks=self.selected_items, request=request)
        elif self.action == 'ship_selected_items':
            self.ship_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        if not self.selected_items:
            message = ('Nothing to do. No manifests have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.manifest_model.objects.filter(
                    pk__in=self.selected_items,
                    shipped=False).delete()
                message = (
                    '{} manifest(s) have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Manifest is not empty.')
                messages.error(self.request, message)

    def ship_selected_items(self):
        """Flags selected items as shipped.
        """
        if not self.selected_items:
            message = ('Nothing to do. No manifests have been selected.')
            messages.warning(self.request, message)
        for manifest in self.manifest_model.objects.filter(pk__in=self.selected_items):
            if manifest.shipped:
                message = (
                    'Manifest has already been shipped. Got {}.'.format(
                        self.manifest.manifest_identifier))
                messages.error(self.request, message)
            else:
                boxes = self.box_model.objects.filter(
                    box_identifier__in=[obj.identifier for obj in manifest.manifestitem_set.all()])
                boxes.update(status=SHIPPED)
                for box in boxes:
                    aliquots = self.aliquot_model.objects.filter(
                        aliquot_identifier__in=[obj.identifier for obj in box.boxitem_set.all()])
                    aliquots.update(shipped=True)
                manifest.shipped = True
                manifest.save()

                message = (
                    'Manifest {} has been shipped.'.format(manifest.manifest_identifier))
                messages.success(self.request, message)
