from datetime import datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

from django.db import models

from edc_visit_schedule.schedule import Schedule


class AppointmentModelStub(Protocol):
    id: UUID | models.UUIDField
    pk: UUID | models.UUIDField
    subject_identifier: str | models.CharField
    appt_datetime: datetime | models.DateTimeField
    visit_code: str | models.CharField
    visit_code_sequence: int | models.IntegerField
    visit_schedule_name: str | models.CharField
    schedule_name: str | models.CharField
    facility_name: str | models.CharField
    timepoint: int | models.IntegerField
    timepoint_datetime: datetime
    schedule: Schedule
    _meta: Any

    objects: models.Manager

    last_visit_code_sequence: int | None
    next: "AppointmentModelStub"
    previous: "AppointmentModelStub"
    get_next: "AppointmentModelStub"

    def save(self, *args, **kwargs) -> None: ...

    def natural_key(self) -> tuple: ...

    def get_previous(self) -> "AppointmentModelStub": ...

    @classmethod
    def related_visit_model_attr(cls) -> str: ...


TAppointmentModelStub = TypeVar("TAppointmentModelStub", bound="AppointmentModelStub")
