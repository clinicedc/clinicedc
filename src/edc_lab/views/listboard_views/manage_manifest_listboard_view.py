from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ..mixins import ManifestViewMixin
from .base_listboard import BaseListboardView, app_config, app_name


class ManifestItemModelWrapper(ModelWrapper):

    model_name = app_config.manifest_item_model
    next_url_name = app_config.manage_manifest_listboard_url_name
    action_name = 'manage'

    @property
    def manifest_identifier(self):
        return self._original_object.manifest.manifest_identifier

    @property
    def box_identifier(self):
        return self._original_object.identifier

    @property
    def box(self):
        return self.box_model.objects.get(box_identifier=self._original_object.identifier)

    @property
    def box_model(self):
        return django_apps.get_model(*app_config.box_model.split('.'))


class ManageManifestListboardView(ManifestViewMixin, BaseListboardView):

    action_name = 'manage'
    navbar_item_selected = 'manifest'
    form_action_url_name = '{}:manage_manifest_item_url'.format(app_name)
    listboard_template_name = app_config.manage_manifest_listboard_template_name
    listboard_url_name = app_config.manage_manifest_listboard_url_name
    model_name = app_config.manifest_item_model
    model_wrapper_class = ManifestItemModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.action_name,
            'manifest_identifier': self.manifest_identifier}
