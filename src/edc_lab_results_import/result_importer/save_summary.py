from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TextIO

from django.core.management import color_style
from django.core.management.color import Style

__all__ = ["SaveSummary"]


@dataclass
class SaveSummary:
    created: int = 0
    skipped: int = 0
    stdout: TextIO = sys.stdout
    style: Style = field(default_factory=color_style)

    def write_summary(self, file_count: int):
        self.write_created_summary(file_count)
        self.stdout.write("  Complete. Dataframe written Result model.\n\n")

    def write_created_summary(self, file_count: int):
        msg = f"  Created {self.created} results from {file_count} files.\n"
        if self.skipped:
            msg += f"   Skipped {self.skipped} duplicates.\n"
        self.stdout.write(self.style.SUCCESS(msg))  # type: ignore[attr-defined]
