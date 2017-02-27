from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper
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
        )
        return context
