from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResolvedValues:
    result_pk: Any
    requisition: Any  # Use the specific Django model class here if possible
    visit_code: str = field(init=False)
    visit_code_sequence: int = field(init=False)
    requisition_identifier: str = field(init=False)
    panel_name: str = field(init=False)

    def __post_init__(self):
        self.visit_code = self.requisition.subject_visit.visit_code
        self.visit_code_sequence = self.requisition.subject_visit.visit_code_sequence
        self.requisition_identifier = self.requisition.requisition_identifier
        self.panel_name = self.requisition.panel.name

        if self.panel_name != self.requisition.panel.name:
            raise ValueError(
                f"Panel name mismatch. {self.panel_name} != {self.requisition.panel.name}"
            )
