from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab import PACKED, Manifest as ManifestObject
from edc_lab.models import Manifest, Box
from edc_lab.labels import BoxLabel
from edc_label import add_job_results_to_messages, LabPrintersMixin

from .action_view import ActionView


class PackView(EdcViewMixin, LabPrintersMixin, ActionView):

    post_action_url = "pack_listboard_url"
    valid_form_actions = [
        "add_selected_to_manifest",
        "remove_selected_items",
        "print_labels",
    ]
    label_cls = BoxLabel

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_manifest = None

    def process_form_action(self, request=None):
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(request, message)
        else:
            if self.action == "remove_selected_items":
                self.remove_selected_items()
            elif self.action == "add_selected_to_manifest":
                if self.selected_manifest:
                    self.add_selected_to_manifest()
            elif self.action == "print_labels":
                job_result = self.print_labels(pks=self.selected_items, request=request)
                if job_result:
                    add_job_results_to_messages(request, [job_result])

    @property
    def selected_manifest(self):
        if not self._selected_manifest:
            if self.request.POST.get("selected_manifest"):
                try:
                    self._selected_manifest = Manifest.objects.get(
                        pk=self.request.POST.get("selected_manifest")
                    )
                except ObjectDoesNotExist:
                    pass
        return self._selected_manifest

    def add_selected_to_manifest(self):
        """Adds the selected items to the selected manifest.
        """
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(self.request, message)
        elif not self.selected_manifest:
            message = "Nothing to do. No manifest has been selected."
            messages.warning(self.request, message)
        else:
            manifest_object = ManifestObject(
                manifest=self.selected_manifest, request=self.request
            )
            try:
                added = 0
                for selected_item in self.selected_items:
                    box = Box.objects.get(pk=selected_item)
                    if manifest_object.add_box(
                        box=box, manifest_item_identifier=box.box_identifier
                    ):
                        added += 1
                        box.status = PACKED
                        box.save()
                    else:
                        break
                if added > 0:
                    message = "{} items have been added to manifest {}.".format(
                        added, self.selected_manifest.human_readable_identifier
                    )
                    messages.success(self.request, message)
            except ProtectedError:
                message = "Unable to remove. Box is not empty."
                messages.error(self.request, message)

    def remove_selected_items(self):
        """Deletes the selected boxes, if allowed.
        """
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(self.request, message)
        else:
            try:
                deleted = Box.objects.filter(pk__in=self.selected_items).delete()
                message = "{} items have been removed.".format(deleted[0])
                messages.success(self.request, message)
            except ProtectedError:
                message = "Unable to remove. Box is not empty."
                messages.error(self.request, message)
