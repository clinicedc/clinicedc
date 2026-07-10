from __future__ import annotations

import sys
from typing import Any

from django.core.management import color_style
from django.db.models import QuerySet

from edc_lab import site_labs
from edc_lab.utils import get_requisition_model

from ..constants import (
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
    NO_MATCH,
    NO_PANEL_FOR_UTEST_ID,
    RESOLVED,
)
from ..models import Result
from .resolve_summary import ResolvedSummary
from .resolved_values import ResolvedValues


class RequisitionResolver:
    def __init__(self):
        self._requisition_by_key: dict[tuple[str, str], list] = {}
        self._resolved_values_list: list[tuple[Any, Any]] = []
        self.ambiguous = 0
        self.ambiguous_updates = list[tuple[Any, str, str, list[str]]]
        self.no_match = 0
        self.no_match_pks: list = []
        self.no_panel_pks: list = []
        self.resolved = 0
        self.summary = ResolvedSummary()
        self.unmapped = 0
        self.untracked = 0
        self.style = color_style()
        self.stdout = sys.stdout

        self.results_without_requisition: QuerySet[Result] = Result.objects.filter(
            requisition_identifier="",
            subject_not_found=False,
            order_datetime__isnull=False,
        ).exclude(subject_identifier="", utestid="")

    def resolve_and_update_results(self):
        if self.results_without_requisition.exists():
            self.update_result_with_requisitions()
            self.update_result_category(self.no_panel_pks, NO_PANEL_FOR_UTEST_ID)
            self.update_result_category(self.no_match_pks, NO_MATCH)
            # self.update_result_if_requisition_ambiguous()
            self.summary = ResolvedSummary(
                resolved=self.resolved,
                ambiguous=self.ambiguous,
                no_match=self.no_match,
                untracked=self.untracked,
                unmapped=self.unmapped,
            )

    def write_summary(self) -> None:
        self.stdout.write(self.style.SUCCESS(self.summary.describe()))

    def update_result_with_requisitions(self) -> None:
        """Update existing Result instances with a requisition and other
        values as provided in ```values_list```.
        """
        RESULT_PK = 0  # noqa: N806
        if self.resolved_values_list:
            updated_result_objs = []
            result_objs = {
                o.pk: o
                for o in Result.objects.filter(
                    pk__in=[v[RESULT_PK] for v in self.resolved_values_list]
                )
            }
            for values in self.resolved_values_list:
                v = ResolvedValues(*values)
                obj = result_objs.get(v.result_pk)
                if not obj:
                    continue
                obj.visit_code = v.visit_code
                obj.visit_code_sequence = v.visit_code_sequence
                obj.requisition_identifier = v.requisition_identifier
                obj.requisition = v.requisition
                obj.subject_visit = v.requisition.subject_visit
                obj.panel_name = v.panel_name
                obj.requisition_ambiguous = False
                obj.requisition_match_category = RESOLVED
                obj.requisition_match_comment = ""
                obj.requisition_candidates = []
                updated_result_objs.append(obj)
            Result.objects.bulk_update(
                updated_result_objs,
                [
                    "visit_code",
                    "visit_code_sequence",
                    "requisition_identifier",
                    "requisition",
                    "subject_visit",
                    "panel_name",
                    "requisition_ambiguous",
                    "requisition_match_category",
                    "requisition_match_comment",
                    "requisition_candidates",
                ],
                batch_size=500,
            )

    @staticmethod
    def update_result_category(pks: list, category: str) -> None:
        """Bulk update unresolved Results (no requisition, no
        candidates).
        """
        if pks:
            Result.objects.filter(pk__in=pks).update(
                requisition_ambiguous=False,
                requisition_match_category=category,
                requisition_match_comment="",
                requisition_candidates=[],
            )

    def update_result_if_requisition_ambiguous(self) -> None:
        if self.ambiguous_updates:
            objs = {
                r.pk: r
                for r in Result.objects.filter(pk__in=[u[0] for u in self.ambiguous_updates])
            }
            for pk, category, comment, candidate_ids in self.ambiguous_updates:
                obj = objs[pk]
                obj.requisition_ambiguous = True
                obj.requisition_match_category = category
                obj.requisition_match_comment = comment
                obj.requisition_candidates = candidate_ids
            Result.objects.bulk_update(
                objs.values(),
                [
                    "requisition_ambiguous",
                    "requisition_match_category",
                    "requisition_match_comment",
                    "requisition_candidates",
                ],
                batch_size=500,
            )

    @property
    def resolved_values_list(self):
        if not self._resolved_values_list:
            for result in self.results_without_requisition.iterator():
                utestid = result.utestid
                panel_names = self.utestid_to_panel_map.get(utestid)
                if not panel_names:
                    self.untracked += 1
                    self.no_panel_pks.append(result.pk)
                    continue

                key = (
                    result.subject_identifier,
                    result.order_datetime.date().isoformat(),
                )
                requisition_candidates: list = [
                    req
                    for req in self.requisition_by_key.get(key, [])
                    if req.panel and req.panel.name in panel_names
                ]

                count = len(requisition_candidates)
                if count == 0:
                    self.no_match += 1
                    self.no_match_pks.append(result.pk)
                elif count > 1:
                    self.ambiguous += 1
                    self.ambiguous_updates.append(
                        self.describe_ambiguous_matches(result, requisition_candidates)
                    )
                else:
                    requisition = requisition_candidates[0]
                    self._resolved_values_list.append((result.pk, requisition))
                    self.resolved += 1
        return self._resolved_values_list

    @property
    def utestid_to_panel_map(self) -> dict[str, set[str]]:
        """Map each utestid to the set of panel names that report it,
        derived from the `site_labs.lab_profiles`.

        For example:
            {
                'glucose': {'blood_glucose'},
                'haemoglobin': {'fbc'},
                 ...
             }
        """
        index: dict[str, set[str]] = {}
        for lab_profile in site_labs.lab_profiles.values():
            for panel in lab_profile.panels.values():
                for utestid in panel.flatten_utestids():
                    index.setdefault(utestid, set()).add(panel.name)
        return index

    @property
    def requisition_by_key(self) -> dict[tuple[str, str], list]:
        if not self._requisition_by_key:
            subject_identifiers = set(
                self.results_without_requisition.values_list(
                    "subject_identifier", flat=True
                ).distinct()
            )
            requisition_model = get_requisition_model()
            for requisition_obj in requisition_model.objects.filter(
                drawn_datetime__isnull=False,
                subject_identifier__in=subject_identifiers,
            ).select_related("panel", "subject_visit"):
                key = (
                    requisition_obj.subject_identifier,
                    requisition_obj.drawn_datetime.date().isoformat(),
                )
                self._requisition_by_key.setdefault(key, []).append(requisition_obj)
        return self._requisition_by_key

    @staticmethod
    def describe_ambiguous_matches(
        result: Result, candidates: Any
    ) -> tuple[Any, str, str, list[str]]:
        """Classify an ambiguous match and capture its contending
        requisitions for later review. Returns
        (pk, category, comment, candidate_identifiers).
        """
        distinct_panels = sorted({r.panel.name for r in candidates if r.panel})
        category = AMBIGUOUS_MULTI_PANEL if len(distinct_panels) > 1 else AMBIGUOUS_SAME_PANEL
        candidate_ids = [r.requisition_identifier for r in candidates]
        comment = (
            f"{len(candidates)} candidate requisition(s) on "
            f"{result.order_datetime.date().isoformat()}; "
            f"panel(s): {', '.join(distinct_panels) or '(none)'}.\n"
        )
        return result.pk, category, comment, candidate_ids
