"""Repair `Result.panel_name` on rows imported before it was written.

`prepare_imported_result` resolved `panel_name` into the dataframe and
then did not persist it, so every result imported before that fix
carries an empty panel. Nothing downstream that joins on panel can work
until this is run: the requisition lookup, the requisition metadata
lookup, and the related-visit fallback in `get_df_result_comparison`.

The panel is a pure lookup from the utest id, the same one the importer
uses, so nothing is guessed here.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TextIO

from django.core.management import color_style
from django.db import transaction

from edc_lab_panel.panels import wbc_differential

from .models import Result
from .utils import get_panel_name_by_utestid

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django.core.management.color import Style

__all__ = ["BackfillSummary", "PanelNameBackfill"]


@dataclass
class BackfillSummary:
    candidates: int = 0
    updated: int = 0
    unmapped: int = 0
    dry_run: bool = False
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def write(self) -> None:
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(f"  Dry run. {self.updated} result(s) would be set.\n")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"  Set panel_name on {self.updated} result(s).\n")
            )
        if self.unmapped:
            self.stdout.write(
                self.style.WARNING(
                    f"   {self.unmapped} left empty, the utest id is in no registered "
                    "panel. See `get_mappings`.\n"
                )
            )


@dataclass
class PanelNameBackfill:
    """Sets `panel_name` from `utestid` on results that have none.

    Saves one result at a time so `simple_history` records the change,
    as `ResultLinker` does and for the same reason. Batched in
    transactions.

    `extra_panels` defaults to the differential panel, matching what
    `import_results` passes. A result whose utest id is in no panel at
    all is counted and left alone, since inventing a panel for it would
    be worse than leaving it visible in `get_df_orphan_results` as
    `panel_unknown`.
    """

    dry_run: bool = False
    batch_size: int = 500
    extra_panels: list | None = None
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def run(self) -> BackfillSummary:
        mapping = get_panel_name_by_utestid(
            self.extra_panels if self.extra_panels is not None else [wbc_differential]
        )
        summary = BackfillSummary(
            candidates=Result.objects.filter(panel_name="").count(),
            dry_run=self.dry_run,
            stdout=self.stdout,
            style=self.style,
        )
        self.stdout.write(f"  Found {summary.candidates} result(s) with no panel.\n")
        for batch in self.get_batches():
            self.update_batch(batch, mapping, summary)
        summary.write()
        return summary

    def get_batches(self) -> Iterator[list[Result]]:
        """Yield one batch at a time, paged by primary key.

        Not by offset: the rows being written leave the `panel_name=""`
        filter as they go, so later rows shift into offsets already
        passed and would be stepped over. A cursor is also the only way
        to hold one batch in memory rather than all of them, which
        matters at a few hundred thousand rows.

        A result whose utest id is in no panel keeps its empty panel and
        so stays in the filter. The cursor steps past it regardless,
        where restarting from the first batch would loop on it forever.
        """
        last_id = None
        while True:
            qs = Result.objects.filter(panel_name="").order_by("id")
            if last_id is not None:
                qs = qs.filter(id__gt=last_id)
            batch = list(qs[: self.batch_size])
            if not batch:
                return
            yield batch
            last_id = batch[-1].id

    def update_batch(self, batch: list[Result], mapping: dict[str, str], summary) -> None:
        if self.dry_run:
            for obj in batch:
                if mapping.get(obj.utestid):
                    summary.updated += 1
                else:
                    summary.unmapped += 1
            return
        with transaction.atomic():
            for obj in batch:
                panel_name = mapping.get(obj.utestid)
                if not panel_name:
                    summary.unmapped += 1
                    continue
                obj.panel_name = panel_name
                obj.save(update_fields=["panel_name"])
                summary.updated += 1
