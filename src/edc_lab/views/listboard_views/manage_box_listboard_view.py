from copy import copy

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator

from .base_box_item_listboard_view import BaseBoxItemListboardView, BaseBoxItemModelWrapper

app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class BoxItemModelWrapper(BaseBoxItemModelWrapper):

    next_url_name = app_config.manage_box_listboard_url_name
    action_name = 'manage'


class ManageBoxListboardView(BaseBoxItemListboardView):

    action_name = 'manage'
    form_action_url_name = '{}:manage_box_item_url'.format(app_name)
    listboard_template_name = app_config.manage_box_listboard_template_name
    listboard_url_name = app_config.manage_box_listboard_url_name
    model_wrapper_class = BoxItemModelWrapper

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
            verify_box_listboard_url=reverse(
                self.verify_box_listboard_url_name,
                kwargs=url_kwargs))
        return context
