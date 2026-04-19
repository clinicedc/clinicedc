from __future__ import annotations

from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext as _

from edc_model_admin.list_filters import FutureDateListFilter
from edc_visit_schedule.exceptions import RegistryNotLoaded
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class CreatedListFilter(FutureDateListFilter):
    title = _("Created")

    parameter_name = "created"
    field_name = "created"


class DueDatetimeListFilter(FutureDateListFilter):
    title = _("Due")

    parameter_name = "due_datetime"
    field_name = "due_datetime"


class FillDatetimeListFilter(FutureDateListFilter):
    title = _("Keyed")

    parameter_name = "fill_datetime"
    field_name = "fill_datetime"


# ---------------------------------------------------------------------------
# In-memory list filters sourced from site_visit_schedules.
#
# Django's default FieldListFilter for a CharField emits
# `SELECT DISTINCT <col> FROM edc_metadata_crfmetadata` on every changelist
# render. With 600k+ rows and the admin's annotation + site WHERE clause, that
# query is not eligible for a MySQL loose index scan and walks the full index.
# Building the option list from the in-process visit schedule registry
# eliminates the query entirely — the registry already holds the authoritative
# set of valid values.
# ---------------------------------------------------------------------------


def _iter_all_visits():
    """Yield (visit_schedule, schedule, visit) across the loaded registry.

    Returns nothing if the registry isn't loaded yet (e.g. during some
    management commands) so admin rendering doesn't blow up.
    """
    try:
        registry = site_visit_schedules.registry
    except RegistryNotLoaded:
        return
    for visit_schedule in registry.values():
        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                yield visit_schedule, schedule, visit


class VisitScheduleNameListFilter(SimpleListFilter):
    title = _("Visit schedule")
    parameter_name = "visit_schedule_name"

    def lookups(self, request, model_admin):  # noqa: ARG002
        names = sorted({vs.name for vs, _, _ in _iter_all_visits()})
        return [(name, name) for name in names]

    def queryset(self, request, queryset):  # noqa: ARG002
        if self.value():
            return queryset.filter(visit_schedule_name=self.value())
        return queryset


class ScheduleNameListFilter(SimpleListFilter):
    title = _("Schedule")
    parameter_name = "schedule_name"

    def lookups(self, request, model_admin):  # noqa: ARG002
        names = sorted({s.name for _, s, _ in _iter_all_visits()})
        return [(name, name) for name in names]

    def queryset(self, request, queryset):  # noqa: ARG002
        if self.value():
            return queryset.filter(schedule_name=self.value())
        return queryset


class VisitCodeListFilter(SimpleListFilter):
    title = _("Visit")
    parameter_name = "visit_code"

    def lookups(self, request, model_admin):  # noqa: ARG002
        codes: set[str] = {visit.code for _, _, visit in _iter_all_visits()}
        return [(code, code) for code in sorted(codes)]

    def queryset(self, request, queryset):  # noqa: ARG002
        if self.value():
            return queryset.filter(visit_code=self.value())
        return queryset


class _DocumentNameListFilterBase(SimpleListFilter):
    """Shared base for CRF/Requisition document_name filters.

    Choices are the verbose_names of every form declared across all
    visits in the registry. Matches how CrfMetadata.document_name is
    populated (source_model_cls._meta.verbose_name).

    Subclasses set `collection_attrs` to select which form collections
    on each Visit to scan.
    """

    title = _("Document")
    parameter_name = "document_name"
    collection_attrs: tuple[str, ...] = ()

    def lookups(self, request, model_admin):  # noqa: ARG002
        verbose_names: set[str] = set()
        for _vs, _sched, visit in _iter_all_visits():
            for attr in self.collection_attrs:
                for form in getattr(visit, attr, []) or []:
                    try:
                        verbose_names.add(str(form.model_cls._meta.verbose_name))
                    except LookupError:
                        # form's model not installed in this deployment — skip
                        continue
        return [(vn, vn) for vn in sorted(verbose_names)]

    def queryset(self, request, queryset):  # noqa: ARG002
        if self.value():
            return queryset.filter(document_name=self.value())
        return queryset


class CrfDocumentNameListFilter(_DocumentNameListFilterBase):
    collection_attrs = ("crfs", "crfs_prn", "crfs_unscheduled", "crfs_missed")


class RequisitionDocumentNameListFilter(_DocumentNameListFilterBase):
    collection_attrs = (
        "requisitions",
        "requisitions_prn",
        "requisitions_unscheduled",
    )
