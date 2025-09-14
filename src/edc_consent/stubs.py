from datetime import datetime
from typing import Protocol

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin

from .model_mixins import ConsentModelMixin


class ConsentModelStub(Protocol):
    subject_identifier: str
    report_datetime: datetime
    ...


class ConsentLikeModel(
    SiteModelMixin,
    ConsentModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    BaseUuidModel,
): ...
