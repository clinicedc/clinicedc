from typing import Any

from edc_dashboard.url_names import url_names
from edc_lab.constants import SHIPPED
from edc_lab.pdf_reports import ManifestPdfReport

from ..listboard_filters import ManifestListboardViewFilters
from .base_listboard_view import BaseListboardView


class ManifestListboardView(BaseListboardView):
    navbar_selected_item = "manifest"

    form_action_url = "manifest_form_action_url"
    listboard_url = "manifest_listboard_url"
    listboard_template = "manifest_listboard_template"
    listboard_model = "edc_lab.manifest"
    listboard_view_permission_codename = "edc_lab_dashboard.view_lab_manifest_listboard"
    listboard_view_only_my_permission_codename = None
    listboard_view_filters = ManifestListboardViewFilters()
    search_form_url = "manifest_listboard_url"
    print_manifest_url = "print_manifest_url"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            new_manifest=self.listboard_model_cls(),
            print_manifest_url_name=url_names.get(self.print_manifest_url),
            SHIPPED=SHIPPED,
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf"):
            response = self.print_manifest()
            return response
        return super().get(request, *args, **kwargs)

    @property
    def manifest(self):
        return self.listboard_model_cls.objects.get(
            manifest_identifier=self.request.GET.get("pdf")
        )

    def print_manifest(self):
        manifest_report = ManifestPdfReport(manifest=self.manifest, user=self.request.user)
        return manifest_report.render_to_response()
