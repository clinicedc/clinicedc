from django.apps import apps as django_apps
from django.contrib import messages
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from ..constants import VERIFIED

app_name = 'edc_lab'


class Manifest:
    """A class of manifest that contains boxes.
    """

    def __init__(self, manifest=None, manifest_identifier=None, request=None):
        self.manifest = manifest
        if not self.manifest:
            self.manifest = Manifest.objects.get(
                manifest_identifier=manifest_identifier)
        self.request = request

    @property
    def app_config(self):
        return django_apps.get_app_config(app_name)

    @property
    def box_model(self):
        return django_apps.get_model(*self.app_config.box_model.split('.'))

    @property
    def manifest_item_model(self):
        return django_apps.get_model(*self.app_config.manifest_item_model.split('.'))

    def add_box(self, box=None, manifest_item_identifier=None):
        """Add a box to the manifest, if possible, and add success or error messages
        to the django message framework.
        """
        added = 0
        if not box:
            message = 'Box does not exist. Got {}.'.format(
                manifest_item_identifier)
            messages.error(self.request, message)
        elif self.validate_box_category(box) and self.validate_box_verified(box):
            try:
                manifest_item = self.manifest_item_model.objects.get(
                    manifest__manifest_identifier=self.manifest.manifest_identifier,
                    identifier=manifest_item_identifier)
            except self.manifest_item_model.DoesNotExist:
                try:
                    manifest_item = self.manifest_item_model.objects.get(
                        identifier=manifest_item_identifier)
                except self.manifest_item_model.DoesNotExist:
                    manifest_item = self.manifest_item_model(
                        manifest=self.manifest,
                        identifier=manifest_item_identifier)
                    manifest_item.save()
                    added = 1
                else:
                    message = mark_safe(
                        'Item is already in a manifest. See <a href="{href}" class="alert-link">'
                        '{manifest_identifier}</a>'.format(
                            href=reverse(
                                self.listboard_url,
                                kwargs={
                                    'manifest_identifier':
                                    manifest_item.manifest.manifest_identifier}),
                            manifest_identifier=manifest_item.manifest.human_readable_identifier))
                    messages.error(self.request, message)
            else:
                message = 'Duplicate item. Got {}.'.format(
                    manifest_item.manifest.human_readable_identifier)
                messages.error(self.request, message)
        return added

    def validate_box_category(self, box=None):
        """Returns True if box category matches manifest category.
        """
        if box.category != self.manifest.category:
            message = 'Invalid category. Manifest accepts {}. Got {}.'.format(
                self.manifest.get_category_display(),
                box.get_category_display())
            messages.error(self.request, message)
            return False
        return True

    def validate_box_verified(self, box=None):
        """Returns True if box status is verified.
        """
        if box.status != VERIFIED:
            message = 'Box is not verified. Got {}.'.format(
                box.human_readable_identifier)
            messages.error(self.request, message)
            return False
        return True
