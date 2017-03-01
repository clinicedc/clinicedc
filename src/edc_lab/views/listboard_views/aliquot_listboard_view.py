from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ...models import BoxItem
from ..listboard_filters import AliquotListboardViewFilters
from .base_listboard import BaseListboardView, app_config, app_name


class AliquotModelWrapper(ModelWrapper):

    model_name = 'edc_lab.aliquot'

    @property
    def human_aliquot_identifier(self):
        return self._original_object.human_aliquot_identifier

    @property
    def box_item(self):
        try:
            return BoxItem.objects.get(identifier=self.aliquot_identifier)
        except BoxItem.DoesNotExist:
            return None


class AliquotListboardView(BaseListboardView):

    navbar_item_selected = 'aliquot'
    model_name = app_config.aliquot_model
    model_wrapper_class = AliquotModelWrapper
    listboard_url_name = app_config.aliquot_listboard_url_name
    listboard_template_name = app_config.aliquot_listboard_template_name
    show_all = True
    listboard_view_filters = AliquotListboardViewFilters()
    form_action_url_name = '{}:aliquot_url'.format(app_name)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
