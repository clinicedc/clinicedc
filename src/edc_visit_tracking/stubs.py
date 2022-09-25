from datetime import datetime
from typing import Protocol, TypeVar, Union

from django.db import models
from edc_model.stubs import ModelMetaStub


class SubjectVisitModelStub(Protocol):
    report_datetime: Union[datetime, models.DateTimeField]
    subject_identifier: Union[str, models.CharField]
    reason: str
    reason_unscheduled: str
    reason_unscheduled_other: str
    visit_code: Union[str, models.CharField]
    visit_code_sequence: Union[int, models.IntegerField]
    visit_schedule: Union[str, models.CharField]
    schedule: Union[str, models.CharField]
    study_status: str
    require_crfs: bool

    objects: models.Manager
    _meta: ModelMetaStub

    def natural_key(self) -> tuple:
        ...

    def save(self, *args, **kwargs) -> None:
        ...

    def related_visit_model_attr(self) -> str:
        ...

    def get_visit_reason_no_follow_up_choices(self) -> list:
        ...

    def get_reason_display(self) -> str:
        ...

    def get_reason_unscheduled_display(self) -> str:
        ...

    def get_require_crfs_display(self) -> str:
        ...

    def update_document_status_on_save(self, update_fields=None) -> None:
        ...


TSubjectVisitModelStub = TypeVar("TSubjectVisitModelStub", bound="SubjectVisitModelStub")
