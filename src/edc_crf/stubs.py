from typing import Iterator, List, Type, TypeVar, Union

from django.db import models
from edc_protocol import Protocol
from edc_visit_tracking.stubs import SubjectVisitModelStub


class MetaModelStub(Protocol):
    verbose_name: str
    fields: Iterator
    ...


class CrfModelStub(Protocol):
    subject_visit: SubjectVisitModelStub

    @classmethod
    def related_visit_model_attr(cls) -> str:
        ...

    objects: models.Manager
    _meta: MetaModelStub
    ...


TCrfModelStub = TypeVar("TCrfModelStub", bound="CrfModelStub")


class MetaModelFormStub(Protocol):
    model: Type[CrfModelStub]
    fields: Union[str, List[str]]
    ...


class CrfModelFormStub(Protocol):
    cleaned_data: dict
    instance: CrfModelStub
    _meta: MetaModelFormStub
    ...
