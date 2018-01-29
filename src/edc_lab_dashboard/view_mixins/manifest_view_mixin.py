from django.apps import apps as django_apps
from django.contrib import messages
from django.utils.html import escape
from django.views.generic.base import ContextMixin


edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ManifestItemError(Exception):
    pass


class ManifestViewMixin(ContextMixin):

    manifest_model = django_apps.get_model(edc_lab_app_config.manifest_model)
    manifest_item_model = django_apps.get_model(
        edc_lab_app_config.manifest_item_model)
    box_model = django_apps.get_model(edc_lab_app_config.box_model)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._manifest = None
        self._manifest_item = None
        self._manifest_identifier = None
        self._manifest_item_identifier = None
        self.original_manifest_item_identifier = None
        self.original_manifest_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'manifest_identifier': self.original_manifest_identifier,
            'manifest_item_identifier': self.original_manifest_item_identifier,
            'manifest': self.manifest,
        })
        return context

    @property
    def manifest_identifier(self):
        if not self._manifest_identifier:
            self.original_manifest_identifier = escape(
                self.kwargs.get('manifest_identifier')).strip()
            self._manifest_identifier = ''.join(
                self.original_manifest_identifier.split('-'))
        return self._manifest_identifier

    @property
    def manifest_item_identifier(self):
        """Returns a cleaned manifest_item_identifier or None.
        """
        if not self._manifest_item_identifier:
            self.original_manifest_item_identifier = escape(
                self.request.POST.get('manifest_item_identifier', '')).strip()
            if self.original_manifest_item_identifier:
                self._manifest_item_identifier = self._clean_manifest_item_identifier()
        return self._manifest_item_identifier

    @property
    def manifest(self):
        if not self._manifest:
            if self.manifest_identifier:
                try:
                    self._manifest = self.manifest_model.objects.get(
                        manifest_identifier=self.manifest_identifier)
                except self.manifest_model.DoesNotExist:
                    self._manifest = None
        return self._manifest

    @property
    def manifest_item(self):
        """Returns a manifest item model instance.
        """
        if not self._manifest_item:
            if self.manifest_item_identifier:
                try:
                    self._manifest_item = self.manifest_item_model.objects.get(
                        manifest=self.manifest,
                        identifier=self.manifest_item_identifier)
                except self.manifest_item_model.DoesNotExist:
                    messages.error(
                        self.request,
                        f'Invalid manifest item. Got {self.original_manifest_item_identifier}')
        return self._manifest_item

    def get_manifest_item(self, position):
        """Returns a manifest item model instance for the given position.
        """
        try:
            manifest_item = self.manifest_item_model.objects.get(
                manifest=self.manifest, position=position)
        except self.manifest_item_model.DoesNotExist:
            messages.error(
                self.request, f'Invalid position for manifest. Got {position}')
            return None
        return manifest_item

    def _clean_manifest_item_identifier(self):
        """Returns a valid identifier or raises.
        """
        manifest_item_identifier = ''.join(
            self.original_manifest_item_identifier.split('-'))
        try:
            self.box_model.objects.get(
                box_identifier=manifest_item_identifier)
        except self.box_model.DoesNotExist:
            messages.error(
                self.request,
                f'Invalid box. Got {self.original_manifest_item_identifier or "None"}.')
        return manifest_item_identifier
