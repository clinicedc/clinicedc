from typing import Any, Optional, Protocol, Type

from django.db.models import Manager, Model, QuerySet
from edc_model.stubs import ModelMetaStub
from edc_visit_schedule import Visit, VisitSchedule
from edc_visit_tracking.stubs import SubjectVisitModelStub


class SubjectVisitLikeModelObject(Protocol):
    appointment: Any
    visits: Any
    metadata: Any
    metadata_destroyer_cls: Any


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
    _meta: ModelMetaStub

    def visit_schedule(self) -> VisitSchedule:
        ...


class CrfMetadataModelStub(Protocol):
    updater_cls = Type["CrfMetadataUpdaterStub"]
    entry_status: str
    metadata_query_options: dict
    model: str
    subject_identifier: str
    timepoint: int
    visit_code: str
    visit_code_sequence: int

    objects: Manager
    visit: VisitModel
    _meta: ModelMetaStub

    def save(self, *args, **kwargs) -> None:
        ...

    def delete(self) -> int:
        ...

    def metadata_visit_object(self) -> Visit:
        ...

    def refresh_from_db(self) -> None:
        ...


class PanelStub(Protocol):
    name: str


class RequisitionMetadataModelStub(Protocol):
    updater_cls = Type["RequisitionMetadataUpdaterStub"]
    entry_status: str
    metadata_query_options: dict
    model: str
    subject_identifier: str
    timepoint: int
    visit_code: str
    visit_code_sequence: int
    panel_name: str

    objects: Manager
    visit: VisitModel
    _meta: ModelMetaStub

    def save(self, *args, **kwargs) -> None:
        ...

    def delete(self) -> int:
        ...

    def metadata_visit_object(self) -> Visit:
        ...

    def metadata_updater_cls(self, **opts: dict):
        ...


class MetadataGetterStub(Protocol):
    metadata_objects: QuerySet
    visit: Optional[SubjectVisitModelStub]


class CrfMetadataUpdaterStub(Protocol):
    ...


class RequisitionMetadataUpdaterStub(Protocol):
    ...


class RequisitionMetadataGetterStub(MetadataGetterStub, Protocol):
    ...


class MetadataWrapperStub(Protocol):
    options: dict
    model_obj: CrfMetadataModelStub
    model_cls: Type[CrfMetadataModelStub]
    ...


class RequisitionMetadataWrapperStub(MetadataWrapperStub, Protocol):
    ...


class Predicate(Protocol):
    @staticmethod
    def get_value(self) -> Any:
        ...
