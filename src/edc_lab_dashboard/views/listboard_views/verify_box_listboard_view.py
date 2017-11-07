from copy import copy
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from edc_lab.constants import SHIPPED

from ...model_wrappers import VerifyBoxItemModelWrapper
from .base_box_item_listboard_view import BaseBoxItemListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')


class VerifyBoxListboardView(BaseBoxItemListboardView):

    action_name = 'verify'
    form_action_url_name = f'edc_lab_dashboard:verify_box_item_url'
    listboard_template_name = app_config.verify_box_listboard_template_name
    listboard_url_name = app_config.verify_box_listboard_url_name
    model_wrapper_cls = VerifyBoxItemModelWrapper
    navbar_selected_item = 'pack'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            manage_box_listboard_url=self.manage_box_listboard_url,
            position=self.kwargs.get('position'),
            SHIPPED=SHIPPED,
        )
        return context

    @property
    def manage_box_listboard_url(self):
        url_kwargs = copy(self.url_kwargs)
        url_kwargs.pop('position')
        url_kwargs['action_name'] = 'manage'
        return reverse(
            self.manage_box_listboard_url_name,
            kwargs=url_kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.action_name,
            'box_identifier': self.box_identifier,
            'position': self.kwargs.get('position', '1')}
