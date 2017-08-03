from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_lab.constants import SHIPPED

from ...model_wrappers import ManifestItemModelWrapper
from ..mixins import ManifestViewMixin
from .base_listboard import BaseListboardView


app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ManageManifestListboardView(ManifestViewMixin, BaseListboardView):

    action_name = 'manage'
    navbar_item_selected = 'manifest'
    form_action_url_name = f'edc_lab_dashboard:manage_manifest_item_url'
    listboard_template_name = app_config.manage_manifest_listboard_template_name
    listboard_url_name = app_config.manage_manifest_listboard_url_name
    model = edc_lab_app_config.manifest_item_model
    model_wrapper_cls = ManifestItemModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(SHIPPED=SHIPPED)
        return context

    @property
    def url_kwargs(self):
        return {
            'action_name': self.action_name,
            'manifest_identifier': self.manifest_identifier}
