from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ...reports import ManifestReport
from .base_listboard import BaseListboardView, app_config, app_name


class ManifestModelWrapper(ModelWrapper):

    model_name = app_config.manifest_model
    next_url_name = app_config.manifest_listboard_url_name


class ManifestListboardView(BaseListboardView):

    navbar_item_selected = 'manifest'

    form_action_url_name = '{}:manifest_url'.format(app_name)
    listboard_url_name = app_config.manifest_listboard_url_name
    listboard_template_name = app_config.manifest_listboard_template_name
    model_name = app_config.manifest_model
    model_wrapper_class = ManifestModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            new_manifest=ManifestModelWrapper.new(),
            print_manifest_url_name='{}:print_manifest_url'.format(app_name),
        )
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get('pdf'):
            response = self.print_manifest()
            return response
        return super().get(request, *args, **kwargs)

    @property
    def manifest(self):
        return self.manifest_model.objects.get(
            manifest_identifier=self.request.GET.get('pdf'))

    def print_manifest(self):
        manifest_report = ManifestReport(manifest=self.manifest)
        return manifest_report.render()
