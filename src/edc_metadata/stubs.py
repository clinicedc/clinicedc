from typing import Any, Protocol, Type

from django.db.models import Manager, Model, QuerySet

from edc_model.stubs import ModelMetaStub
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_tracking.stubs import RelatedVisitModelStub


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

    def visit_schedule(self) -> VisitSchedule: ...  # noqa


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

    def save(self, *args, **kwargs) -> None: ...  # noqa

    def delete(self) -> int: ...  # noqa

    def metadata_visit_object(self) -> Visit: ...  # noqa

    def refresh_from_db(self) -> None: ...  # noqa


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

    def save(self, *args, **kwargs) -> None: ...  # noqa

    def delete(self) -> int: ...

    def metadata_visit_object(self) -> Visit: ...  # noqa

    def metadata_updater_cls(self, **opts: dict): ...  # noqa


class MetadataGetterStub(Protocol):
    metadata_objects: QuerySet
    visit: RelatedVisitModelStub | None


class CrfMetadataUpdaterStub(Protocol): ...  # noqa


class RequisitionMetadataUpdaterStub(Protocol): ...  # noqa


class RequisitionMetadataGetterStub(MetadataGetterStub, Protocol): ...  # noqa


class MetadataWrapperStub(Protocol):
    options: dict
    model_obj: CrfMetadataModelStub
    model_cls: Type[CrfMetadataModelStub]
    ...  # noqa


class RequisitionMetadataWrapperStub(MetadataWrapperStub, Protocol): ...  # noqa


class Predicate(Protocol):
    @staticmethod
    def get_value(self) -> Any: ...  # noqa
