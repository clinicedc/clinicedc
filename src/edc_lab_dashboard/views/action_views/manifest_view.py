from django.contrib import messages
from django.db.models.deletion import ProtectedError
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab import SHIPPED
from edc_lab.models import Box, Aliquot, Manifest
from edc_lab.labels import ManifestLabel
from edc_label import add_job_results_to_messages, LabPrintersMixin

from ...view_mixins import ManifestViewMixin
from .action_view import ActionView


class ManifestView(EdcViewMixin, ManifestViewMixin, LabPrintersMixin, ActionView):

    post_action_url = "manifest_listboard_url"
    valid_form_actions = [
        "remove_selected_items",
        "print_labels",
        "ship_selected_items",
    ]
    label_cls = ManifestLabel

    def process_form_action(self, request=None):
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(request, message)
        else:
            if self.action == "remove_selected_items":
                self.remove_selected_items()
            elif self.action == "print_labels":
                job_result = self.print_labels(pks=self.selected_items, request=request)
                if job_result:
                    add_job_results_to_messages(request, [job_result])
            elif self.action == "ship_selected_items":
                self.ship_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        try:
            deleted = Manifest.objects.filter(
                pk__in=self.selected_items, shipped=False
            ).delete()
            message = f"{deleted[0]} manifest(s) have been removed."
            messages.success(self.request, message)
        except ProtectedError:
            message = "Unable to remove. Manifest is not empty."
            messages.error(self.request, message)

    def ship_selected_items(self):
        """Flags selected items as shipped.
        """
        for manifest in Manifest.objects.filter(pk__in=self.selected_items):
            if manifest.shipped:
                message = (
                    f"Manifest has already been shipped. "
                    f"Got {manifest.manifest_identifier}."
                )
                messages.error(self.request, message)
            else:
                boxes = Box.objects.filter(
                    box_identifier__in=[
                        obj.identifier for obj in manifest.manifestitem_set.all()
                    ]
                )
                boxes.update(status=SHIPPED)
                for box in boxes:
                    aliquots = Aliquot.objects.filter(
                        aliquot_identifier__in=[
                            obj.identifier for obj in box.boxitem_set.all()
                        ]
                    )
                    aliquots.update(shipped=True)
                manifest.shipped = True
                manifest.save()

                message = f"Manifest {manifest.manifest_identifier} has been shipped."
                messages.success(self.request, message)
