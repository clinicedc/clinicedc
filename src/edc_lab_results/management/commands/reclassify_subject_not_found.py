"""Reclassify unresolved (subject_not_found) Results.

Splits the existing unresolved pile into SUBJECT_NOT_FOUND (a well-formed
identifier for this protocol/site whose subject just isn't registered ->
reissue-able) vs OUT_OF_SCOPE (wrong protocol, unregistered site, or junk).
Runs the same classify_identifier logic as import, without re-parsing PDFs.

Usage::

    manage.py reclassify_subject_not_found
"""

from __future__ import annotations

from collections import Counter

from django.core.management.base import BaseCommand

from edc_lab_results.constants import OUT_OF_SCOPE, SUBJECT_NOT_FOUND
from edc_lab_results.import_results import category_for_unresolved
from edc_lab_results.models import Result

BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Reclassify unresolved results into SUBJECT_NOT_FOUND vs OUT_OF_SCOPE."

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        qs = Result.objects.filter(subject_not_found=True)
        total = qs.count()
        if not total:
            self.stdout.write("No unresolved results to reclassify.")
            return

        self.stdout.write(f"Reclassifying {total} unresolved result(s) ...")
        cache: dict[str, tuple[str, str]] = {}
        counts: Counter = Counter()
        batch: list[Result] = []

        for result in qs.iterator():
            if result.name_id not in cache:
                cache[result.name_id] = category_for_unresolved(result.name_id)
            category, comment = cache[result.name_id]
            counts[category] += 1
            if (
                result.requisition_match_category != category
                or result.requisition_match_comment != comment
            ):
                result.requisition_match_category = category
                result.requisition_match_comment = comment
                batch.append(result)
            if len(batch) >= BATCH_SIZE:
                Result.objects.bulk_update(
                    batch, ["requisition_match_category", "requisition_match_comment"]
                )
                batch.clear()

        if batch:
            Result.objects.bulk_update(
                batch, ["requisition_match_category", "requisition_match_comment"]
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Reclassified: {counts.get(SUBJECT_NOT_FOUND, 0)} subject_not_found "
                f"(reissue-able), {counts.get(OUT_OF_SCOPE, 0)} out_of_scope."
            )
        )
