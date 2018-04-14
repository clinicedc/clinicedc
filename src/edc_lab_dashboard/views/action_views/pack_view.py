from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab import PACKED, BoxLabel, Manifest as ManifestObject
from edc_label import add_job_results_to_messages

from ...view_mixins import ModelsViewMixin
from .action_view import ActionView

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class PackView(EdcBaseViewMixin, ModelsViewMixin, ActionView):

    post_action_url = 'pack_listboard_url'
    valid_form_actions = [
        'add_selected_to_manifest', 'remove_selected_items', 'print_labels']
    box_model = django_apps.get_model(*edc_lab_app_config.box_model.split('.'))
    label_cls = BoxLabel
    manifest_model = 'edc_lab.manifest'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_manifest = None

    def process_form_action(self, request=None):
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(request, message)
        else:
            if self.action == 'remove_selected_items':
                self.remove_selected_items()
            elif self.action == 'add_selected_to_manifest':
                if self.selected_manifest:
                    self.add_selected_to_manifest()
            elif self.action == 'print_labels':
                job_result = self.print_labels(
                    pks=self.selected_items, request=request)
                if job_result:
                    add_job_results_to_messages(request, [job_result])

    @property
    def selected_manifest(self):
        if not self._selected_manifest:
            if self.request.POST.get('selected_manifest'):
                model_cls = django_apps.get_model(self.manifest_model)
                try:
                    self._selected_manifest = model_cls.objects.get(
                        pk=self.request.POST.get('selected_manifest'))
                except ObjectDoesNotExist:
                    pass
        return self._selected_manifest

    def add_selected_to_manifest(self):
        """Adds the selected items to the selected manifest.
        """
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        elif not self.selected_manifest:
            message = ('Nothing to do. No manifest has been selected.')
            messages.warning(self.request, message)
        else:
            manifest_object = ManifestObject(
                manifest=self.selected_manifest,
                request=self.request)
            try:
                added = 0
                for selected_item in self.selected_items:
                    box = self.box_model.objects.get(pk=selected_item)
                    if manifest_object.add_box(
                            box=box,
                            manifest_item_identifier=box.box_identifier):
                        added += 1
                        box.status = PACKED
                        box.save()
                    else:
                        break
                if added > 0:
                    message = (
                        '{} items have been added to manifest {}.'.format(
                            added,
                            self.selected_manifest.human_readable_identifier))
                    messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Box is not empty.')
                messages.error(self.request, message)

    def remove_selected_items(self):
        """Deletes the selected boxes, if allowed.
        """
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
                message = ('Unable to remove. Box is not empty.')
                messages.error(self.request, message)
