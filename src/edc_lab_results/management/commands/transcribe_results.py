from __future__ import annotations

from django.core.management.base import BaseCommand

from ...models import Result
from ...transcribe import transcribe_results
from ...transcribe.discovery import discover_crf_models


class Command(BaseCommand):
    help = "Transcribe imported lab results onto CRF models."

    def add_arguments(self, parser: object) -> None:
        parser.add_argument(
            "--order-no",
            type=str,
            help="Transcribe results for a specific order number.",
        )
        parser.add_argument(
            "--subject-identifier",
            type=str,
            help="Transcribe results for a specific subject.",
        )
        parser.add_argument(
            "--visit-code",
            type=str,
            help="Visit code (used with --subject-identifier).",
        )
        parser.add_argument(
            "--all-pending",
            action="store_true",
            help="Transcribe all results not yet transcribed.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be done without saving.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show details for all results including skipped.",
        )

    def handle(self, **options: object) -> None:
        order_no = options["order_no"]
        subject_identifier = options["subject_identifier"]
        visit_code = options["visit_code"]
        all_pending = options["all_pending"]
        dry_run = options["dry_run"]
        self.verbose = options["verbose"]

        qs = self._build_queryset(order_no, subject_identifier, visit_code, all_pending)
        if qs is None:
            return

        count = qs.count()
        if not count:
            self.stdout.write("No results to transcribe.")
            return

        mode = "DRY RUN" if dry_run else "LIVE"
        self.stdout.write(f"\n[{mode}] Processing {count} result(s)...\n")

        if self.verbose:
            self._print_discovered_crfs()

        summary = transcribe_results(qs, dry_run=dry_run)
        self._print_summary(summary, dry_run)

    def _build_queryset(
        self,
        order_no: str | None,
        subject_identifier: str | None,
        visit_code: str | None,
        all_pending: bool,
    ) -> object | None:
        if order_no:
            return Result.objects.filter(order_no=order_no)
        if subject_identifier:
            qs = Result.objects.filter(subject_identifier=subject_identifier)
            if visit_code:
                qs = qs.filter(visit_code=visit_code)
            return qs
        if all_pending:
            return Result.objects.filter(
                transcribed_datetime__isnull=True,
                utest_id__gt="",
                subject_identifier__gt="",
                visit_code__gt="",
            )
        self.stderr.write(
            "Error: Specify --order-no, --subject-identifier, or --all-pending."
        )
        return None

    def _print_discovered_crfs(self) -> None:
        crf_models = discover_crf_models()
        self.stdout.write("--- Discovered CRF models ---")
        for panel_name, info in sorted(crf_models.items()):
            verbose_name = info.model._meta.verbose_name  # noqa: SLF001
            utest_ids = ", ".join(info.utest_ids) if info.utest_ids else "(none)"
            self.stdout.write(f"  {verbose_name} [{panel_name}]")
            self.stdout.write(f"    utest_ids: {utest_ids}")
        self.stdout.write("")

    def _print_summary(self, summary: object, dry_run: bool) -> None:
        self.stdout.write("\n--- Summary ---")
        self.stdout.write(f"  Transcribed:     {summary.transcribed}")
        self.stdout.write(f"  Already correct: {summary.already_correct}")
        self.stdout.write(f"  Discrepancies:   {summary.discrepancies}")
        self.stdout.write(f"  CRFs created:    {summary.crf_created}")
        self.stdout.write(f"  No visit found:  {summary.no_visit}")
        self.stdout.write(f"  No requisition:  {summary.no_requisition}")
        self.stdout.write(f"  Skipped:         {summary.skipped}")

        if summary.discrepancy_details:
            self.stdout.write("\n--- Discrepancies ---")
            for d in summary.discrepancy_details:
                self.stdout.write(
                    f"  {d.subject_identifier} {d.visit_code}.{d.visit_code_sequence} "
                    f"{d.panel_name}/{d.utest_id}: {d.message}"
                )

        if self.verbose:
            skipped = [d for d in summary.details if d.status == "skipped"]
            if skipped:
                self.stdout.write("\n--- Skipped ---")
                for d in skipped:
                    self.stdout.write(
                        f"  {d.subject_identifier} {d.visit_code}.{d.visit_code_sequence} "
                        f"{d.panel_name}/{d.utest_id}: {d.message}"
                    )
            correct = [d for d in summary.details if d.status == "already_correct"]
            if correct:
                self.stdout.write("\n--- Already correct ---")
                for d in correct:
                    self.stdout.write(
                        f"  {d.subject_identifier} {d.visit_code}.{d.visit_code_sequence} "
                        f"{d.panel_name}/{d.utest_id}: {d.imported_value} {d.imported_units}"
                    )
            transcribed = [d for d in summary.details if d.status == "transcribed"]
            if transcribed:
                self.stdout.write("\n--- Transcribed ---")
                for d in transcribed:
                    self.stdout.write(
                        f"  {d.subject_identifier} {d.visit_code}.{d.visit_code_sequence} "
                        f"{d.panel_name}/{d.utest_id}: {d.imported_value} {d.imported_units}"
                    )

        if dry_run:
            self.stdout.write("\n(Dry run — no changes saved.)\n")
        else:
            self.stdout.write("")
