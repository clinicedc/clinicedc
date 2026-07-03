"""Re-run requisition matching over unlinked Results.

Runs LabResultImporter.link_requisitions() without re-parsing any PDFs, so
matcher changes (or corrected utest_id mappings) can be applied to already
imported Results. Only Results with an empty requisition_identifier are
(re)processed.

Usage::

    manage.py relink_requisitions
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from edc_lab_results.import_results import LabResultImporter


class Command(BaseCommand):
    help = "Re-run requisition matching over unlinked Results (no PDF re-parse)."

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        self.stdout.write("Re-running requisition matching ...")
        summary = LabResultImporter.link_requisitions()
        self.stdout.write(
            self.style.SUCCESS(
                f"Requisition matching: {summary.linked} matched, "
                f"{summary.ambiguous} ambiguous (flagged), "
                f"{summary.no_match} no match, "
                f"{summary.untracked} untracked (no panel), "
                f"{summary.unmapped} unmapped (no utest_id)."
            )
        )
