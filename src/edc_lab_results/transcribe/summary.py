from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class TranscribeDetail:
    """Detail record for a single transcription action."""

    subject_identifier: str
    visit_code: str
    visit_code_sequence: int
    panel_name: str
    utest_id: str
    status: str  # transcribed, discrepancy, already_correct, skipped
    imported_value: Decimal | None = None
    imported_units: str = ""
    existing_value: Decimal | None = None
    existing_units: str = ""
    message: str = ""


@dataclass
class TranscribeSummary:
    """Aggregated summary of a transcription run."""

    transcribed: int = 0
    discrepancies: int = 0
    already_correct: int = 0
    no_requisition: int = 0
    crf_created: int = 0
    no_visit: int = 0
    skipped: int = 0
    details: list[TranscribeDetail] = field(default_factory=list)

    def add(self, detail: TranscribeDetail) -> None:
        self.details.append(detail)
        if detail.status == "transcribed":
            self.transcribed += 1
        elif detail.status == "discrepancy":
            self.discrepancies += 1
        elif detail.status == "already_correct":
            self.already_correct += 1
        elif detail.status == "skipped":
            self.skipped += 1

    @property
    def discrepancy_details(self) -> list[TranscribeDetail]:
        return [d for d in self.details if d.status == "discrepancy"]
