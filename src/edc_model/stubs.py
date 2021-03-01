from typing import Protocol, TypeVar
from uuid import UUID

from django.db import models
from django_audit_fields.stubs import AuditModelStub


class ModelMetaStub(Protocol):
    verbose_name: str
    verbose_name_plural: str
    label_lower: str
    object_name: str
    app_label: str
    model_name: str

    def get_fields(self) -> list:
        ...


class BaseUuidModelStub(AuditModelStub, Protocol):
    id: UUID
    admin_url_name: str
    admin_site_name: str

    def get_absolute_url(self) -> str:
        ...

    objects: models.Manager
    _meta: ModelMetaStub

    ...


TBaseUuidModelStub = TypeVar("TBaseUuidModelStub", bound="BaseUuidModelStub")


class BaseUuidHistoryModelStub(AuditModelStub, Protocol):
    id: UUID
    admin_url_name: str
    admin_site_name: str

    def get_absolute_url(self) -> str:
        ...

    objects: models.Manager
    history: models.Manager
    _meta: ModelMetaStub

    ...
