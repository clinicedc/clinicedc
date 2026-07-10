from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import TextIO

from django.core.management import color_style
from django.core.management.color import Style

__all__ = ["SaveSummary"]


@dataclass
class SaveSummary:
    created: int = 0
    skipped: int = 0
    skipped_out_of_scope: int = 0  # not stored (EDC_LAB_RESULTS_SKIP_OUT_OF_SCOPE)
    unresolved: int = 0  # total unresolved (subject_not_found + out_of_scope)
    subject_not_found: int = 0  # reissue-able (this protocol/site, or screening)
    out_of_scope: int = 0  # wrong protocol / unregistered site / junk
    reasons: Counter = field(default_factory=Counter)
    unrecognized_units: set[tuple[str, str]] = field(default_factory=set)
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def write_summary(self, file_count: int):
        self.write_created_summary(file_count)
        self.write_unresolved_summary()
        self.write_unrecognized_units_summary()

    def write_created_summary(self, file_count: int):
        msg = f"Created {self.created} results from {file_count} files.\n"
        if self.skipped:
            msg += f" Skipped {self.skipped} duplicates.\n"
        self.stdout.write(self.style.SUCCESS(msg))  # type: ignore[attr-defined]

    def write_unresolved_summary(self):
        if self.unresolved:
            self.stdout.write(
                self.style.WARNING(  # type: ignore[attr-defined]
                    f"{self.unresolved} results could not be resolved: "
                    f"{self.subject_not_found} subject_not_found \n"
                )
            )
            for reason, count in self.reasons.most_common():
                self.stdout.write(f"  {reason or '(none)'}: {count}\n")

    def write_unrecognized_units_summary(self):
        if self.unrecognized_units:
            self.stdout.write(
                self.style.WARNING(  # type: ignore[attr-defined]
                    "The following units could not be converted "
                    "(no matching NormalData formula or conversion path):\n"
                )
            )
            for utestid, units in sorted(self.unrecognized_units):
                self.stdout.write(f"  {utestid}: {units}\n")
