from datetime import datetime
from typing import Any, Optional, Protocol, Type, TypeVar, Union
from uuid import UUID

from django.db import models
from edc_visit_schedule import Schedule


class VisitModelStub(Protocol):
    visit_code: Union[str, models.CharField]
    visit_code_sequence: Union[int, models.IntegerField]
    visit_schedule_name: Union[str, models.CharField]


class AppointmentModelStub(Protocol):
    id: Union[UUID, models.UUIDField]
    pk: Union[UUID, models.UUIDField]
    subject_identifier: Union[str, models.CharField]
    appt_datetime: Union[datetime, models.DateTimeField]
    visit_code: Union[str, models.CharField]
    visit_code_sequence: Union[int, models.IntegerField]
    visit_schedule_name: Union[str, models.CharField]
    schedule_name: Union[str, models.CharField]
    facility_name: Union[str, models.CharField]
    timepoint: Union[int, models.IntegerField]
    timepoint_datetime: datetime
    schedule: Schedule
    visit_model_cls: Type[models.Model]
    _meta: Any

    objects: models.Manager
    visit: VisitModelStub

    last_visit_code_sequence: Optional[int]
    next: "AppointmentModelStub"
    previous: "AppointmentModelStub"

    def save(self, *args, **kwargs) -> None:
        ...

    def natural_key(self) -> tuple:
        ...

    def get_previous(self) -> "AppointmentModelStub":
        ...

    @classmethod
    def related_visit_model_attr(cls) -> str:
        ...


TAppointmentModelStub = TypeVar("TAppointmentModelStub", bound="AppointmentModelStub")
