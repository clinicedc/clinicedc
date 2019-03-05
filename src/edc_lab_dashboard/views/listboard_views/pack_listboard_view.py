from django.apps import apps as django_apps
from edc_constants.constants import OPEN
from edc_lab.constants import SHIPPED
from edc_lab.models import Manifest, Box

from ...model_wrappers import BoxModelWrapper
from ..listboard_filters import PackListboardViewFilters
from .base_listboard_view import BaseListboardView

app_config = django_apps.get_app_config("edc_lab_dashboard")
edc_lab_app_config = django_apps.get_app_config("edc_lab")


class PackListboardView(BaseListboardView):

    form_action_url = "pack_form_action_url"
    listboard_url = "pack_listboard_url"
    listboard_template = "pack_listboard_template"
    listboard_model = Box
    listboard_view_permission_codename = "edc_dashboard.view_lab_pack_listboard"
    listboard_view_only_my_permission_codename = None
    model_wrapper_cls = BoxModelWrapper
    navbar_selected_item = "pack"
    listboard_view_filters = PackListboardViewFilters()
    search_form_url = "pack_listboard_url"

    @property
    def open_manifests(self):
        return Manifest.objects.filter(status=OPEN).order_by("-manifest_datetime")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            new_box=BoxModelWrapper(Box()),
            open_manifests=self.open_manifests,
            SHIPPED=SHIPPED,
        )
        return context
