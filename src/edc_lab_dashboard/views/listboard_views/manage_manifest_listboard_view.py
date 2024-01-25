from typing import Any

from edc_lab.constants import SHIPPED

from ...view_mixins import ManifestViewMixin
from .base_listboard_view import BaseListboardView


class ManageManifestListboardView(ManifestViewMixin, BaseListboardView):
    action_name = "manage"
    navbar_selected_item = "manifest"
    form_action_url = "manage_manifest_item_form_action_url"
    listboard_url = "manage_manifest_listboard_url"
    listboard_template = "manage_manifest_listboard_template"
    listboard_view_permission_codename = "edc_lab_dashboard.view_lab_manifest_listboard"
    search_form_url = "manage_manifest_listboard_url"

    listboard_model = "edc_lab.manifestitem"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(SHIPPED=SHIPPED, paginator_url_kwargs=self.url_kwargs)
        return super().get_context_data(**kwargs)

    @property
    def url_kwargs(self):
        return {
            "action_name": self.action_name,
            "manifest_identifier": self.manifest_identifier,
        }
