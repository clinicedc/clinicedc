from dataclasses import dataclass


@dataclass
class ResolvedSummary:
    resolved: int = 0
    ambiguous: int = 0
    no_match: int = 0
    untracked: int = 0  # utestid not on any panel
    unmapped: int = 0  # no EDC utestid at all

    def describe(self) -> str:
        return (
            f"\nRequisition matching:\n {self.resolved} matched \n"
            f"{self.ambiguous} ambiguous (flagged) \n"
            f"{self.no_match} no match \n"
            f"{self.untracked} untracked (no panel) \n"
            f"{self.unmapped} unmapped (no utestid).\n"
        )
