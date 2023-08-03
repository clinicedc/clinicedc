from __future__ import annotations

from typing import Any, Generic, Protocol, Tuple, Type, TypeVar
from uuid import UUID

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import ForeignObjectRel, Model
from django.db.models.manager import BaseManager
from django.forms import Field
from edc_appointment.models import Appointment
from edc_metadata.metadata import Destroyer, Metadata
from edc_metadata.metadata_rules import MetadataRuleEvaluator
from edc_visit_schedule import Schedule, VisitCollection, VisitSchedule
from edc_visit_schedule.typing_stubs import VisitScheduleFieldsProtocol

_M = TypeVar("_M", bound=Model)
_Self = TypeVar("_Self", bound=Model)


class ModelBase(type):
    @property
    def objects(cls: type[_Self]) -> BaseManager[_Self]:
        ...

    @property
    def _default_manager(cls: type[_Self]) -> BaseManager[_Self]:
        ...

    @property
    def _base_manager(cls: type[_Self]) -> BaseManager[_Self]:
        ...


class Options(Generic[_M]):
    def label_lower(self) -> str:
        ...

    def fields(self) -> Tuple[Field]:
        ...

    def get_fields(
        self, include_parents: bool = ..., include_hidden: bool = ...
    ) -> list[Field | ForeignObjectRel | GenericForeignKey]:
        ...


class SiteFieldsProtocol(Protocol):
    def id(self) -> int:
        ...

    def name(self) -> str | None:
        ...


class RelatedVisitProtocol(VisitScheduleFieldsProtocol, Protocol):
    metadata_cls: Type[Metadata]
    metadata_destroyer_cls: Type[Destroyer]
    metadata_rule_evaluator_cls: Type[MetadataRuleEvaluator]

    class Meta:
        ...

    _meta: Options[Any]

    def id(self) -> UUID:
        ...

    def appointment(self) -> Appointment:
        ...

    def subject_identifier(self) -> str | None:
        ...

    def reason(self) -> str | None:
        ...

    def consent_version(self) -> str | None:
        ...

    def site(self) -> SiteFieldsProtocol:
        ...

    @property
    def metadata_query_options(self) -> dict:
        ...

    @property
    def visit_schedule(self) -> VisitSchedule:
        ...

    @property
    def schedule(self) -> Schedule:
        ...

    def visits(self) -> VisitCollection:
        ...
