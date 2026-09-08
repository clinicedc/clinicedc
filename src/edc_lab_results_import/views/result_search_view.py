from __future__ import annotations

import contextlib
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import NoReverseMatch, reverse
from django.views.generic.base import TemplateView

from edc_dashboard.url_names import InvalidDashboardUrlName, url_names
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab_results.utils import get_result_model_cls
from edc_metadata.models import CrfMetadata
from edc_navbar import NavbarViewMixin

from ..models import Result
from ..view_utils import ResultComparison, ResultCrfButton

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.db import models


class ResultSearchView(
    PermissionRequiredMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """A DataTable-driven search page for imported lab `Result` records.

    A `subject_identifier`, `screening_identifier` or
    `requisition_identifier` is required before any rows are queried:
    `Result` is not site/study scoped, so an unfiltered query could
    return every imported result across the trial. Any one may be given,
    and giving more narrows further. Results imported before a screening
    identifier could be resolved to a subject carry only the former, so
    all three are searchable.

    Once results are loaded, visit code, utestid and result_datetime are
    narrowed client-side via DataTables.

    Each row carries a group key, `requisition|source_file`, and one
    add/change button is rendered for each group. Which button, if any,
    is offered is decided client-side: the rows left visible by the
    DataTables filters must resolve to a single group, that is to a
    single result file and requisition, and so to a single subject,
    timepoint and panel. See `result_search.html`.
    """

    template_name = "edc_lab_results_import/result_search.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_lab_results_import.view_result"
    search_fields = (
        "subject_identifier",
        "screening_identifier",
        "requisition_identifier",
    )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        search_terms = self.get_search_terms()
        results = self.get_results(search_terms)
        for result in results:
            result.group_key = self.get_group_key(result)
        crf_buttons = self.get_crf_buttons(
            results, requisition_identifier=search_terms["requisition_identifier"]
        )
        kwargs.update(
            **search_terms,
            searched=any(search_terms.values()),
            results=results,
            crf_buttons=crf_buttons,
            comparisons=self.get_comparisons(results, crf_buttons),
            dashboard_buttons=self.get_dashboard_buttons(results),
        )
        return kwargs

    def get_search_terms(self) -> dict[str, str]:
        """Return the search term for each search field.

        The url kwargs are how a CRF returns to this page once saved,
        with the search criteria form filled in as it was left. See
        `ResultCrfButton`.

        A querystring, which is how the search form submits, always
        wins over the url kwargs, and wins as a whole. Otherwise a
        field cleared on the form would be refilled from the url of the
        search the user is trying to leave.
        """
        source = self.kwargs
        if any(field in self.request.GET for field in self.search_fields):
            source = self.request.GET
        return {field: (source.get(field) or "").strip() for field in self.search_fields}

    @staticmethod
    def get_results(search_terms: dict[str, str]) -> list[Result]:
        """Return the results matching the given search terms.

        Returns nothing where no search term is given. `Result` is not
        site/study scoped, so an unfiltered query could return every
        imported result across the trial.
        """
        opts = {f"{field}__icontains": term for field, term in search_terms.items() if term}
        if not opts:
            return []
        return list(
            Result.objects.filter(**opts)
            .select_related(
                "requisition__panel",
                "subject_visit__appointment",
                "source_document",
            )
            .order_by("-result_datetime")
        )

    @staticmethod
    def get_group_key(result: Result) -> str:
        """Return the key of the result set this row belongs to.

        The requisition alone determines the subject, the timepoint and
        the panel, and so the result CRF. The source file is included so
        that two documents resolving to one requisition, for example an
        original and a corrected report, are never merged into a single
        CRF without the user narrowing the search first.
        """
        return f"{result.requisition_id or ''}|{result.source_file}"

    def get_crf_buttons(
        self, results: list[Result], requisition_identifier: str | None = None
    ) -> list[ResultCrfButton]:
        """Return one add/change button per result set.

        A button is offered only for a result set resolved to both a
        requisition and a related visit, whose panel has a result CRF,
        and where the CRF metadata exists for that timepoint.

        `requisition_identifier` is the search term that produced these
        results, if any. It is carried into the button's `next` url so
        that saving the CRF returns to this same search.
        """
        groups: dict[str, Result] = {}
        for result in results:
            if result.requisition_id and result.subject_visit_id and result.source_file:
                groups.setdefault(self.get_group_key(result), result)
        candidates: dict[str, tuple[Result, type[models.Model]]] = {}
        for group_key, result in groups.items():
            panel_name = getattr(result.requisition.panel, "name", None)
            if model_cls := get_result_model_cls(panel_name):
                candidates.update({group_key: (result, model_cls)})
        metadata = self.get_metadata(candidates.values())
        buttons: list[ResultCrfButton] = []
        for group_key, (result, model_cls) in candidates.items():
            metadata_model_obj = metadata.get(self.get_metadata_key(result, model_cls))
            if not metadata_model_obj:
                continue
            buttons.append(
                ResultCrfButton(
                    metadata_model_obj=metadata_model_obj,
                    appointment=result.subject_visit.appointment,
                    user=self.request.user,
                    current_site=self.request.site,
                    requisition_id=result.requisition_id,
                    requisition_identifier=requisition_identifier or "",
                    group_key=group_key,
                )
            )
        return buttons

    def get_comparisons(
        self, results: list[Result], crf_buttons: list[ResultCrfButton]
    ) -> list[ResultComparison]:
        """Return one comparison per result set that has a result CRF.

        There is nothing to compare until the CRF exists, so result sets
        offered an add button are skipped. The CRF instance was already
        fetched to build the button, so this costs no further queries.
        """
        results_by_group: dict[str, list[Result]] = defaultdict(list)
        for result in results:
            results_by_group[self.get_group_key(result)].append(result)
        comparisons = []
        for btn in crf_buttons:
            if not btn.model_obj:
                continue
            comparison = ResultComparison(
                model_obj=btn.model_obj,
                results=results_by_group[btn.group_key],
                group_key=btn.group_key,
            )
            if comparison.rows:
                comparisons.append(comparison)
        return comparisons

    @staticmethod
    def get_metadata_key(result: Result, model_cls: type[models.Model]) -> tuple[str, ...]:
        subject_visit = result.subject_visit
        return (
            subject_visit.subject_identifier,
            subject_visit.visit_schedule_name,
            subject_visit.schedule_name,
            subject_visit.visit_code,
            str(subject_visit.visit_code_sequence),
            model_cls._meta.label_lower,
        )

    def get_metadata(
        self, candidates: Iterable[tuple[Result, type[models.Model]]]
    ) -> dict[tuple[str, ...], CrfMetadata]:
        """Return the CrfMetadata for all candidate result sets, keyed
        by timepoint and model, fetched in a single query.
        """
        candidates = list(candidates)
        if not candidates:
            return {}
        qs = CrfMetadata.objects.filter(
            subject_identifier__in={r.subject_visit.subject_identifier for r, _ in candidates},
            model__in={m._meta.label_lower for _, m in candidates},
            visit_code__in={r.subject_visit.visit_code for r, _ in candidates},
        )
        return {
            (
                obj.subject_identifier,
                obj.visit_schedule_name,
                obj.schedule_name,
                obj.visit_code,
                str(obj.visit_code_sequence),
                obj.model,
            ): obj
            for obj in qs
        }

    @staticmethod
    def get_dashboard_buttons(results: list[Result]) -> list[dict[str, str]]:
        """Return one subject dashboard button per subject in the
        result set.

        Offered as a fallback where the visible rows cannot be resolved
        to a single result set, but do resolve to a single subject.
        """
        buttons: list[dict[str, str]] = []
        try:
            url_name = url_names.get("subject_dashboard_url")
        except InvalidDashboardUrlName:
            return buttons
        subject_identifiers = {r.subject_identifier for r in results if r.subject_identifier}
        for subject_identifier in sorted(subject_identifiers):
            with contextlib.suppress(NoReverseMatch):
                buttons.append(
                    dict(
                        subject_identifier=subject_identifier,
                        url=reverse(
                            url_name, kwargs=dict(subject_identifier=subject_identifier)
                        ),
                    )
                )
        return buttons
