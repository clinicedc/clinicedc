from copy import copy

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from edc_lab.constants import SHIPPED

from ...model_wrappers import ManageBoxItemModelWrapper
from ...dashboard_urls import dashboard_urls
from .base_box_item_listboard_view import BaseBoxItemListboardView


class ManageBoxListboardView(BaseBoxItemListboardView):

    action_name = 'manage'
    form_action_url = 'manage_box_item_action_url'
    listboard_url = 'manage_box_listboard_url'
    listboard_template = 'manage_box_listboard_template'
    verify_box_listboard_url = dashboard_urls.get('verify_box_listboard_url')
    model_wrapper_cls = ManageBoxItemModelWrapper
    navbar_selected_item = 'pack'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.action_name,
            'box_identifier': self.box_identifier}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_kwargs = copy(self.url_kwargs)
        url_kwargs['position'] = 1
        url_kwargs['action_name'] = 'verify'
        context.update(
            verify_box_listboard_url_reversed=reverse(
                self.verify_box_listboard_url,
                kwargs=url_kwargs))
        return context
