from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from .base_listboard import BaseListboardView, app_config, app_name


class BoxModelWrapper(ModelWrapper):

    model_name = app_config.box_model
    next_url_name = app_config.pack_listboard_url_name


class PackListboardView(BaseListboardView):

    form_action_url_name = '{}:pack_url'.format(app_name)
    listboard_url_name = app_config.pack_listboard_url_name
    listboard_template_name = app_config.pack_listboard_template_name
    model_name = app_config.box_model
    model_wrapper_class = BoxModelWrapper
    navbar_item_selected = 'pack'
    shipped = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            new_box=BoxModelWrapper.new(),
            shipped=self.shipped,
        )
        return context
