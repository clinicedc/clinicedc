from typing import Any, Protocol

from django.db.models import Manager, Model


class VisitModel(Protocol):
    """A typical EDC subject visit model"""

    metadata_query_options: dict
    reason: str
    schedule_name: str
    site: Model
    subject_identifier: str
    visit_code: str
    visit_code_sequence: int
    visit_schedule_name: str
    _meta: Any


class CrfMetadataModel(Protocol):
    entry_status: str
    metadata_query_options: dict
    objects: Manager
    subject_identifier: str

    def save(self, *args, **kwargs) -> None:
        ...


class RequisitionMetadataModel(Protocol):
    entry_status: str
    metadata_query_options: dict
    objects: Manager
    subject_identifier: str

    def save(self, *args, **kwargs) -> None:
        ...
