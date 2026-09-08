from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TextIO

import pandas as pd
from django.core.management import color_style
from django.db import transaction

from ..constants import RESOLVER_MISS
from ..dataframes import get_df_orphan_results
from ..models import Result

if TYPE_CHECKING:
    from django.core.management.color import Style

__all__ = ["LinkSummary", "ResultLinker"]

# fields the link writes. `subject_visit` is written too: without it
# `ResultSearchView.get_crf_buttons` will not offer a CRF button, so a
# result linked to a requisition but not to a visit is still unusable
LINKED_FIELDS = (
    "requisition_id",
    "requisition_identifier",
    "requisition_datetime",
    "subject_visit_id",
)


@dataclass
class LinkSummary:
    candidates: int = 0
    linked: int = 0
    conflicts: int = 0
    unchanged: int = 0
    dry_run: bool = False
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def write(self) -> None:
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(f"  Dry run. {self.linked} result(s) would be linked.\n")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"  Linked {self.linked} result(s).\n"))
        if self.unchanged:
            self.stdout.write(f"   Skipped {self.unchanged}, already linked.\n")
        if self.conflicts:
            self.stdout.write(
                self.style.WARNING(
                    f"   {self.conflicts} linked to a requisition saying no result was "
                    "expected. Review these.\n"
                )
            )


@dataclass
class ResultLinker:
    """Writes the requisition already found by `get_df_orphan_results`
    back onto the orphaned results.

    Saves one result at a time so `simple_history` records every change
    and the link stays reversible from the audit trail. `bulk_update`
    would be faster and would skip `save()`, the historical record, the
    audit fields and every signal, which is the wrong trade for imported
    lab data. Batched in transactions so a failure part way through does
    not leave half a batch written.

    Reads the report itself rather than taking an exported one. A
    requisition edited since a worklist was exported, `result_expected`
    set to NO for instance, would make that worklist wrong. See
    `results_changed_since`.
    """

    dry_run: bool = False
    batch_size: int = 500
    subject_identifier: str | None = None
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def run(self) -> LinkSummary:
        df = self.get_df()
        summary = LinkSummary(
            candidates=len(df),
            conflicts=int(df["result_expected_conflict"].sum()) if not df.empty else 0,
            dry_run=self.dry_run,
            stdout=self.stdout,
            style=self.style,
        )
        self.stdout.write(f"  Found {summary.candidates} result(s) to link.\n")
        for batch in self.get_batches(df):
            self.link_batch(batch, summary)
        summary.write()
        return summary

    def get_df(self) -> pd.DataFrame:
        """Return the orphans whose requisition already exists."""
        df = get_df_orphan_results()
        if df.empty:
            return df
        df = df[df["bucket"] == RESOLVER_MISS]
        if self.subject_identifier:
            df = df[df["subject_identifier"] == self.subject_identifier]
        return df.reset_index(drop=True)

    def get_batches(self, df: pd.DataFrame) -> list[pd.DataFrame]:
        if df.empty:
            return []
        return [
            df.iloc[pos : pos + self.batch_size] for pos in range(0, len(df), self.batch_size)
        ]

    def link_batch(self, batch: pd.DataFrame, summary: LinkSummary) -> None:
        if self.dry_run:
            summary.linked += len(batch)
            return
        with transaction.atomic():
            for row in batch.itertuples(index=False):
                if self.link(row):
                    summary.linked += 1
                else:
                    summary.unchanged += 1

    @staticmethod
    def link(row: Any) -> bool:
        """Link one result. Returns False if there was nothing to do.

        Re-reads the result rather than trusting the frame: the report
        may have been built moments ago, but this is the write, and a
        result linked in the meantime must not be relinked.
        """
        obj = Result.objects.get(id=row.result_id)
        if obj.requisition_id:
            return False
        obj.requisition_id = row.requisition_id
        obj.requisition_identifier = row.requisition_identifier
        obj.requisition_datetime = none_if_na(row.requisition_datetime)
        obj.subject_visit_id = row.subject_visit_id
        # `AuditModelMixin.save` extends update_fields with the audit
        # fields, so `modified` moves and `results_changed_since` sees
        # this run. `simple_history` writes its record on post_save,
        # which `update_fields` does not narrow
        obj.save(update_fields=list(LINKED_FIELDS))
        return True


def none_if_na(value: Any) -> Any:
    """Return None for NaT or NaN, which a date field cannot take."""
    return None if pd.isna(value) else value
