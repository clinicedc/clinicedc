"""Set `Result.panel_name` on rows imported before it was persisted.

Usage::
    manage.py backfill_panel_name --dry-run
    manage.py backfill_panel_name

"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from edc_lab_results_import.backfill import PanelNameBackfill


class Command(BaseCommand):
    """Set `Result.panel_name` from `utestid`.

    Nothing that joins on panel works until this has run. See
    `get_df_orphan_results` and `get_df_result_comparison`.
    """

    help = "Set Result.panel_name from utestid on results that have none."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Report what would be set without writing.",
        )
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=500,
            help="Results per transaction. Default 500.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        PanelNameBackfill(
            dry_run=options["dry_run"],
            batch_size=options["batch_size"],
            stdout=self.stdout,
        ).run()
