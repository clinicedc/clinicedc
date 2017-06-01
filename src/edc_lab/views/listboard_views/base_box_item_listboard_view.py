from edc_model_wrapper import ModelWrapper

from ..mixins import BoxViewMixin
from .base_listboard import BaseListboardView, app_config


class BaseBoxItemModelWrapper(ModelWrapper):

    model_name = app_config.box_item_model
    action_name = None
    next_url_name = None
    next_url_attrs = {
        'edc_lab.boxitem': ['box_identifier', 'action_name']}
    url_instance_attrs = ['box_identifier', 'action_name']

    @property
    def human_readable_identifier(self):
        return self._original_object.human_readable_identifier

    @property
    def box_identifier(self):
        return self._original_object.box.box_identifier


class BaseBoxItemListboardView(BoxViewMixin, BaseListboardView):

    navbar_item_selected = 'pack'
    ordering = ('-position', )
    model_name = app_config.box_item_model

    def get_queryset_filter_options(self, request, *args, **kwargs):
        return {'box': self.box}
