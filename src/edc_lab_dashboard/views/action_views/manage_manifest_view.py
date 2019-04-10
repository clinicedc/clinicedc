from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab import Manifest as ManifestObject
from edc_lab.models import ManifestItem, Box

from ...view_mixins import ManifestViewMixin
from .action_view import ActionView


class ManageManifestViewError(Exception):
    pass


class ManageManifestView(EdcViewMixin, ManifestViewMixin, ActionView):

    post_action_url = "manage_manifest_listboard_url"
    valid_form_actions = ["add_item", "remove_selected_items"]

    @property
    def url_kwargs(self):
        return {
            "action_name": self.kwargs.get("action_name"),
            "manifest_identifier": self.manifest_identifier,
        }

    def process_form_action(self, request=None):
        if self.action == "add_item":
            if self.manifest and self.manifest_item_identifier:
                self.add_item()
        elif self.action == "remove_selected_items":
            self.remove_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(self.request, message)
        elif ManifestItem.objects.filter(
            pk__in=self.selected_items, manifest__shipped=True
        ).exists():
            message = "Unable to remove. Some selected items have already been shipped."
            messages.error(self.request, message)
        else:
            try:
                deleted = ManifestItem.objects.filter(
                    pk__in=self.selected_items, manifest__shipped=False
                ).delete()
                message = "{} items have been removed.".format(deleted[0])
                messages.success(self.request, message)
            except ProtectedError:
                message = "Unable to remove. Manifest is not empty."
                messages.error(self.request, message)

    def add_item(self):
        """Adds the box to the manifest if validated.
        """
        manifest_object = ManifestObject(manifest=self.manifest, request=self.request)
        manifest_object.add_box(
            box=self.box, manifest_item_identifier=self.manifest_item_identifier
        )

    @property
    def box(self):
        try:
            return Box.objects.get(box_identifier=self.manifest_item_identifier)
        except ObjectDoesNotExist:
            return None
