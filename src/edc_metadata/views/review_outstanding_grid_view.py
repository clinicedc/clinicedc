from __future__ import annotations

from urllib.parse import urlencode

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.urls import reverse
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_sites.site import sites
from edc_visit_schedule.exceptions import RegistryNotLoaded
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import CRF, REQUIRED
from ..models import (
    CrfMetadata,
    CrfMetadataUnavailable,
    CrfPriority,
    RequisitionMetadata,
    RequisitionMetadataUnavailable,
)
from ..view_mixins import SiteScopeViewMixin

CRF_COLLECTION_ATTRS = ("crfs", "crfs_prn", "crfs_unscheduled", "crfs_missed")


def _iter_registry():
    """Yield (visit_schedule, schedule) across the loaded registry."""
    try:
        registry = site_visit_schedules.registry
    except RegistryNotLoaded:
        return
    for visit_schedule in registry.values():
        for schedule in visit_schedule.schedules.values():
            yield visit_schedule, schedule


def schedule_choices() -> list[tuple[str, str]]:
    """[(value, label)] where value is 'visit_schedule_name::schedule_name'."""
    choices: list[tuple[str, str]] = []
    seen: set[str] = set()
    for visit_schedule, schedule in _iter_registry():
        value = f"{visit_schedule.name}::{schedule.name}"
        if value not in seen:
            seen.add(value)
            choices.append((value, f"{visit_schedule.name} / {schedule.name}"))
    return choices


def visit_columns(visit_schedule_name: str, schedule_name: str) -> list[tuple[str, str]]:
    """[(visit_code, visit_title)] ordered for the selected schedule."""
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    schedule = visit_schedule.schedules.get(schedule_name)
    return [(visit.code, visit.title) for visit in schedule.visits.values()]


def crf_model_choices(visit_schedule_name: str, schedule_name: str) -> list[tuple[str, str]]:
    """[(model_label, verbose_name)] for CRFs declared in the schedule."""
    seen: dict[str, str] = {}
    for visit_schedule, schedule in _iter_registry():
        if visit_schedule.name != visit_schedule_name or schedule.name != schedule_name:
            continue
        for visit in schedule.visits.values():
            for attr in CRF_COLLECTION_ATTRS:
                for form in getattr(visit, attr, []) or []:
                    try:
                        seen[form.model] = str(form.model_cls._meta.verbose_name)
                    except LookupError:
                        seen.setdefault(form.model, form.model)
    return sorted(seen.items(), key=lambda kv: kv[1])


def model_verbose_name(label: str) -> str:
    try:
        return str(django_apps.get_model(label)._meta.verbose_name)
    except LookupError:
        return label


class ReviewOutstandingGridView(
    PermissionRequiredMixin,
    SiteScopeViewMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """A data-manager review screen aggregating outstanding (REQUIRED) CRFs
    and requisitions at the subject x visit grain, with a CRF leaderboard
    lens for prioritising follow-up.
    """

    template_name = "edc_metadata/review_outstanding_grid.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_metadata.view_crfmetadata"
    paginate_by = 25

    def get_context_data(self, **kwargs) -> dict:
        kwargs = super().get_context_data(**kwargs)
        visit_schedule_name, schedule_name = self.selected_schedule()
        kwargs.update(
            REQUIRED=REQUIRED,
            schedule_choices=schedule_choices(),
            selected_schedule=(
                f"{visit_schedule_name}::{schedule_name}" if visit_schedule_name else ""
            ),
            site_choices=self.site_choices(),
            selected_site_value=self.selected_site_value(),
            lens=self.lens(),
        )
        if not visit_schedule_name:
            kwargs.update(no_schedule=True)
            return kwargs

        site_ids = self.selected_site_ids()
        columns = visit_columns(visit_schedule_name, schedule_name)
        models, priority_only, configured = self.priority_models(
            visit_schedule_name, schedule_name
        )
        tier_map = self.tier_map(visit_schedule_name, schedule_name)
        visit_code = self.request.GET.get("visit_code") or None
        subject_q = self.request.GET.get("q", "").strip()

        crf_base = self.base_filter(
            site_ids, visit_schedule_name, schedule_name, visit_code, subject_q
        )
        if models:
            crf_base["model__in"] = models
        # requisitions are not narrowed by the CRF priority set (those are CRF
        # model labels); requisition prioritisation is deferred.
        req_base = self.base_filter(
            site_ids, visit_schedule_name, schedule_name, visit_code, subject_q
        )

        # When a CRF set is active (priority or ad-hoc override) the view is
        # CRF-focused: requisitions are excluded from the subject set, cells
        # and totals so the filter isn't muddied by unrelated requisitions
        # (requisition prioritisation is deferred).
        crf_only = bool(models)

        # items flagged "data unavailable" drop out of the outstanding counts
        crf_exclude = self._flagged_ids(CrfMetadata, CrfMetadataUnavailable, crf_base)
        req_exclude = (
            set()
            if crf_only
            else self._flagged_ids(
                RequisitionMetadata, RequisitionMetadataUnavailable, req_base, panel=True
            )
        )

        kwargs.update(
            columns=columns,
            crf_model_choices=crf_model_choices(visit_schedule_name, schedule_name),
            selected_models=models or [],
            priority_only_checked=priority_only,
            no_priority_configured=priority_only and not configured,
            selected_visit_code=visit_code or "",
            subject_q=subject_q,
            crf_only=crf_only,
            unavailable_count=len(crf_exclude) + len(req_exclude),
            filter_querystring=self._filter_querystring(),
        )
        if self.lens() == "grid":
            kwargs.update(
                **self.grid(
                    crf_base,
                    req_base,
                    columns,
                    visit_schedule_name,
                    schedule_name,
                    crf_only,
                    crf_exclude,
                    req_exclude,
                )
            )
        else:
            kwargs.update(
                leaderboard=self.leaderboard(
                    site_ids,
                    visit_schedule_name,
                    schedule_name,
                    models,
                    columns,
                    tier_map,
                    subject_q,
                    crf_exclude,
                )
            )
        return kwargs

    # ------------------------------------------------------------------ params
    def lens(self) -> str:
        return "grid" if self.request.GET.get("lens") == "grid" else "leaderboard"

    def priority_only_requested(self) -> bool:
        """Default on. A submitted filter form (marker `submitted`) with the
        checkbox cleared turns it off."""
        if self.request.GET.get("submitted"):
            return self.request.GET.get("priority_only") == "1"
        return True

    def selected_schedule(self) -> tuple[str | None, str | None]:
        choices = schedule_choices()
        valid = {value for value, _ in choices}
        value = self.request.GET.get("schedule")
        if value not in valid:
            value = choices[0][0] if choices else None
        if not value:
            return None, None
        visit_schedule_name, schedule_name = value.split("::", 1)
        return visit_schedule_name, schedule_name

    def site_choices(self) -> list[tuple[int, str]]:
        qs = Site.objects.filter(id__in=self.allowed_site_ids()).order_by("name")
        return [(site.id, sites.get(site.id).title) for site in qs]

    def selected_site_value(self) -> str:
        """The raw site selection: "" means all allowed sites."""
        value = self.request.GET.get("site")
        if value == "":
            return ""
        try:
            value = int(value)
        except (TypeError, ValueError):
            # default (param absent) -> current site
            return str(self.request.site.id)
        return str(value) if value in self.allowed_site_ids() else ""

    def selected_site_ids(self) -> list[int]:
        """Effective site ids to filter on (a single chosen site, or all
        allowed sites when "All sites" is selected)."""
        value = self.selected_site_value()
        if value == "":
            return self.allowed_site_ids()
        return [int(value)]

    @staticmethod
    def base_filter(
        site_ids, visit_schedule_name, schedule_name, visit_code, subject_q=None
    ) -> dict:
        opts = dict(
            entry_status=REQUIRED,
            site_id__in=site_ids,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
        )
        if visit_code:
            opts["visit_code"] = visit_code
        if subject_q:
            opts["subject_identifier__icontains"] = subject_q
        return opts

    def priority_models(
        self, visit_schedule_name: str, schedule_name: str
    ) -> tuple[list[str] | None, bool, bool]:
        """Return (models_or_None, priority_only_effective, configured_exists).

        An ad-hoc `models` querystring overrides the persisted set. Otherwise
        the active CRF priority rows for the schedule are used. Falls back to
        all models (None) with a banner when priority-only is on but nothing
        is configured.
        """
        ad_hoc = [m for m in self.request.GET.getlist("models") if m]
        if ad_hoc:
            return ad_hoc, True, True
        priority_only = self.priority_only_requested()
        configured = list(
            CrfPriority.objects.filter(
                active=True,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name,
                metadata_kind=CRF,
            ).values_list("model", flat=True)
        )
        if priority_only and configured:
            return configured, True, bool(configured)
        return None, priority_only, bool(configured)

    @staticmethod
    def tier_map(visit_schedule_name: str, schedule_name: str) -> dict[str, int]:
        return dict(
            CrfPriority.objects.filter(
                active=True,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name,
                metadata_kind=CRF,
            ).values_list("model", "tier")
        )

    # ------------------------------------------------------------------ queries
    @staticmethod
    def _flagged_ids(model_cls, unavailable_cls, base: dict, panel: bool = False) -> set:
        """Metadata ids flagged 'data unavailable' within the request scope.

        Flags are exceptions (few), so resolving their natural keys to a bounded
        Q-OR and `.exclude(id__in=...)` keeps the board queries simple.
        """
        flags = unavailable_cls.objects.filter(
            visit_schedule_name=base["visit_schedule_name"],
            schedule_name=base["schedule_name"],
            site_id__in=base["site_id__in"],
        )
        if base.get("visit_code"):
            flags = flags.filter(visit_code=base["visit_code"])
        if base.get("subject_identifier__icontains"):
            flags = flags.filter(
                subject_identifier__icontains=base["subject_identifier__icontains"]
            )
        key_fields = ["subject_identifier", "visit_code", "visit_code_sequence", "model"]
        if panel:
            key_fields.append("panel_name")
        q = Q()
        found = False
        for row in flags.values(*key_fields):
            q |= Q(**row)
            found = True
        if not found:
            return set()
        return set(model_cls.objects.filter(q, **base).values_list("id", flat=True))

    @staticmethod
    def _subject_totals(
        model_cls, base: dict, exclude_ids: set | None = None
    ) -> dict[str, int]:
        qs = model_cls.objects.filter(**base)
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)
        return {
            row["subject_identifier"]: row["n"]
            for row in qs.values("subject_identifier").annotate(n=Count("id")).order_by()
        }

    @staticmethod
    def _cell_counts(
        model_cls, base: dict, subject_ids: list[str], exclude_ids: set | None = None
    ) -> dict[tuple, int]:
        qs = model_cls.objects.filter(**base, subject_identifier__in=subject_ids)
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)
        return {
            (row["subject_identifier"], row["visit_code"]): row["n"]
            for row in qs.values("subject_identifier", "visit_code")
            .annotate(n=Count("id"))
            .order_by()
        }

    @staticmethod
    def _column_counts(
        model_cls, base: dict, exclude_ids: set | None = None
    ) -> dict[str, int]:
        qs = model_cls.objects.filter(**base)
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)
        return {
            row["visit_code"]: row["n"]
            for row in qs.values("visit_code").annotate(n=Count("id")).order_by()
        }

    # ------------------------------------------------------------------ builders
    def grid(
        self,
        crf_base,
        req_base,
        columns,
        visit_schedule_name,
        schedule_name,
        crf_only,
        crf_exclude,
        req_exclude,
    ) -> dict:
        crf_totals = self._subject_totals(CrfMetadata, crf_base, crf_exclude)
        # CRF-focused view (a CRF set is active): exclude requisitions entirely.
        req_totals = (
            {}
            if crf_only
            else self._subject_totals(RequisitionMetadata, req_base, req_exclude)
        )
        totals: dict[str, int] = {}
        for source in (crf_totals, req_totals):
            for subject, n in source.items():
                totals[subject] = totals.get(subject, 0) + n
        # predictable, stable order by subject identifier
        ordered = sorted(totals)

        paginator = Paginator(ordered, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        page_subjects = list(page_obj.object_list)

        crf_cells = self._cell_counts(CrfMetadata, crf_base, page_subjects, crf_exclude)
        req_cells = (
            {}
            if crf_only
            else self._cell_counts(RequisitionMetadata, req_base, page_subjects, req_exclude)
        )

        visit_codes = [code for code, _ in columns]
        rows = []
        for subject in page_subjects:
            cells = []
            for visit_code in visit_codes:
                crf_n = crf_cells.get((subject, visit_code), 0)
                req_n = req_cells.get((subject, visit_code), 0)
                url = (
                    reverse(
                        "edc_metadata:metadata_detail_url",
                        kwargs=dict(
                            subject_identifier=subject,
                            visit_schedule_name=visit_schedule_name,
                            schedule_name=schedule_name,
                            visit_code=visit_code,
                        ),
                    )
                    if (crf_n + req_n)
                    else None
                )
                cells.append(dict(crf=crf_n, req=req_n, total=crf_n + req_n, url=url))
            rows.append(
                dict(subject_identifier=subject, cells=cells, total=totals.get(subject, 0))
            )

        crf_cols = self._column_counts(CrfMetadata, crf_base, crf_exclude)
        req_cols = (
            {} if crf_only else self._column_counts(RequisitionMetadata, req_base, req_exclude)
        )
        column_totals = []
        grand_total = 0
        for visit_code in visit_codes:
            total = crf_cols.get(visit_code, 0) + req_cols.get(visit_code, 0)
            grand_total += total
            column_totals.append(total)

        return dict(
            grid=rows,
            column_totals=column_totals,
            grand_total=grand_total,
            page_obj=page_obj,
            paginator=paginator,
            page_range=list(
                paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
            ),
            subject_count=len(ordered),
        )

    def leaderboard(
        self,
        site_ids,
        visit_schedule_name,
        schedule_name,
        models,
        columns,
        tier_map,
        subject_q=None,
        exclude_ids=None,
    ) -> list[dict]:
        opts = dict(
            entry_status=REQUIRED,
            site_id__in=site_ids,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
        )
        if models:
            opts["model__in"] = models
        if subject_q:
            opts["subject_identifier__icontains"] = subject_q
        qs = CrfMetadata.objects.filter(**opts)
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)
        rows_qs = (
            qs.values("model", "visit_code")
            .annotate(subjects=Count("subject_identifier", distinct=True))
            .order_by()
        )
        pivot: dict[str, dict[str, int]] = {}
        totals: dict[str, int] = {}
        for row in rows_qs:
            pivot.setdefault(row["model"], {})[row["visit_code"]] = row["subjects"]
            totals[row["model"]] = totals.get(row["model"], 0) + row["subjects"]

        visit_codes = [code for code, _ in columns]
        schedule_value = f"{visit_schedule_name}::{schedule_name}"
        site_value = self.selected_site_value()
        leaderboard = []
        ordered = sorted(totals, key=lambda m: (tier_map.get(m, 99), -totals[m], m))
        for model_label in ordered:
            cells = []
            for visit_code in visit_codes:
                count = pivot.get(model_label, {}).get(visit_code, 0)
                handoff = "?" + urlencode(
                    [
                        ("lens", "grid"),
                        ("submitted", "1"),
                        ("schedule", schedule_value),
                        ("site", site_value),
                        ("models", model_label),
                        ("visit_code", visit_code),
                    ]
                )
                cells.append(dict(count=count, url=handoff if count else None))
            leaderboard.append(
                dict(
                    model=model_label,
                    verbose_name=model_verbose_name(model_label),
                    tier=tier_map.get(model_label),
                    cells=cells,
                    total=totals[model_label],
                )
            )
        return leaderboard

    # ------------------------------------------------------------------ links
    def _filter_querystring(self) -> str:
        """Current filter params (no page/lens) for building links."""
        get = self.request.GET
        # `site` carries a meaningful empty value ("All sites"), so emit the
        # resolved selection explicitly rather than skipping it when falsy —
        # otherwise "All sites" is lost across pagination/lens links.
        params: list[tuple[str, str]] = [("site", self.selected_site_value())]
        params += [
            (key, get.get(key))
            for key in ("schedule", "submitted", "priority_only", "visit_code", "q")
            if get.get(key)
        ]
        params += [("models", model) for model in get.getlist("models") if model]
        return urlencode(params)
