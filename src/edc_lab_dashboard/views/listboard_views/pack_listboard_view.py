from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_constants.constants import OPEN
from edc_lab.constants import SHIPPED
from edc_lab.models import Manifest, Box

from ...model_wrappers import BoxModelWrapper
from ..listboard_filters import PackListboardViewFilters
from .base_listboard_view import BaseListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class PackListboardView(BaseListboardView):

    form_action_url_name = f'edc_lab_dashboard:pack_url'
    listboard_url_name = app_config.pack_listboard_url_name
    listboard_template_name = app_config.pack_listboard_template_name
    model = edc_lab_app_config.box_model
    manifest_model_name = edc_lab_app_config.manifest_model
    model_wrapper_cls = BoxModelWrapper
    navbar_selected_item = 'pack'
    listboard_view_filters = PackListboardViewFilters()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def open_manifests(self):
        return Manifest.objects.filter(status=OPEN).order_by('-manifest_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            new_box=BoxModelWrapper(Box()),
            open_manifests=self.open_manifests,
            SHIPPED=SHIPPED,
        )
        return context
