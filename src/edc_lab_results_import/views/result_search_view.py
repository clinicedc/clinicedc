from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..models import Result


class ResultSearchView(
    PermissionRequiredMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """A DataTable-driven search page for imported lab `Result` records.

    A `subject_identifier` or `screening_identifier` is required before
    any rows are queried: `Result` is not site/study scoped, so an
    unfiltered query could return every imported result across the
    trial. Either may be given, and giving both narrows further. Results
    imported before a screening identifier could be resolved to a
    subject carry only the former, so both are searchable.

    Once results are loaded, visit code, utestid and result_datetime are
    narrowed client-side via DataTables.
    """

    template_name = "edc_lab_results_import/result_search.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_lab_results_import.view_result"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        subject_identifier = (self.request.GET.get("subject_identifier") or "").strip()
        screening_identifier = (self.request.GET.get("screening_identifier") or "").strip()
        opts: dict[str, str] = {}
        if subject_identifier:
            opts.update(subject_identifier__icontains=subject_identifier)
        if screening_identifier:
            opts.update(screening_identifier__icontains=screening_identifier)
        results = (
            Result.objects.filter(**opts)
            .select_related("requisition", "subject_visit")
            .order_by("-result_datetime")
            if opts
            else Result.objects.none()
        )

        kwargs.update(
            subject_identifier=subject_identifier,
            screening_identifier=screening_identifier,
            searched=bool(opts),
            results=results,
        )
        return kwargs
