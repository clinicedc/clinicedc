"""Link imported results back to the requisition that already exists.

Only the `resolver_miss` bucket of `get_df_orphan_results`: results
carrying no requisition where one is already keyed at their timepoint
for their panel. `RequisitionModelMixin.Meta` constrains panel and
related visit to be unique together, so the target is determined, not
guessed, and nothing here matches on a date.

Usage::
    manage.py link_orphan_results --dry-run
    manage.py link_orphan_results
    manage.py link_orphan_results --batch-size 200

"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from edc_lab_results_import.result_linker import ResultLinker


class Command(BaseCommand):
    """Link orphaned imported results to their existing requisition.

    Reads `get_df_orphan_results` itself rather than taking an exported
    worklist, so it can never act on a stale one. See
    `results_changed_since`.
    """

    help = "Link orphaned imported results to their existing requisition."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Report what would be linked without writing.",
        )
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=500,
            help="Results to link per transaction. Default 500.",
        )
        parser.add_argument(
            "--subject-identifier",
            dest="subject_identifier",
            default=None,
            help="Limit to one subject. Useful for a first run.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        ResultLinker(
            dry_run=options["dry_run"],
            batch_size=options["batch_size"],
            subject_identifier=options["subject_identifier"],
            stdout=self.stdout,
        ).run()
