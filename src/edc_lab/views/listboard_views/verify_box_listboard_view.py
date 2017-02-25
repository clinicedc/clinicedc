from copy import copy

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator

from .base_listboard import app_config, app_name
from .base_box_item_listboard_view import BaseBoxItemListboardView, BaseBoxItemModelWrapper


class BoxItemModelWrapper(BaseBoxItemModelWrapper):

    next_url_name = app_config.verify_box_listboard_url_name
    action_name = 'verify'


class VerifyBoxListboardView(BaseBoxItemListboardView):

    action_name = 'verify'
    form_action_url_name = '{}:verify_box_item_url'.format(app_name)
    listboard_template_name = app_config.verify_box_listboard_template_name
    listboard_url_name = app_config.verify_box_listboard_url_name
    model_wrapper_class = BoxItemModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reverse_kwargs = copy(self.reverse_kwargs)
        reverse_kwargs.pop('position')
        reverse_kwargs['action_name'] = 'manage'
        context.update(
            manage_box_listboard_url=reverse(
                self.manage_box_listboard_url_name,
                kwargs=reverse_kwargs),
            position=self.kwargs.get('position'))
        return context

    @property
    def url_kwargs(self):
        return {
            'action_name': self.action_name,
            'box_identifier': self.box_identifier,
            'position': self.kwargs.get('position', '1')}
