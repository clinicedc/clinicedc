from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


class ModelStub(Protocol):
    def save(self, *args, **kwargs):
        ...


class SubjectScreeningModelStub(ModelStub, Protocol):
    eligibility_cls: Any
    identifier_cls: Any
    screening_identifier_field_name: str

    id: UUID
    screening_identifier: str
    subject_identifier: str
    subject_identifier_as_pk: UUID
    report_datetime: datetime
    gender: str
    age_in_years: int
    eligible: bool
    reasons_ineligible: str
    ...

    def get_report_datetime_for_eligibility_datetime(self) -> datetime:
        ...
