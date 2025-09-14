from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from edc_visit_tracking.typing_stubs import RelatedVisitProtocol

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin
    from edc_metadata.models import CrfMetadata, RequisitionMetadata


class MetadataWrapperError(Exception):
    pass


class MetadataWrapper:
    """A class that wraps the corresponding model instance, or not, for the
    given metadata object and sets it to itself along with other
    attributes like the visit, model class, metadata_obj, etc.
    """

    label: str | None = None

    def __init__(
        self,
        visit: RelatedVisitProtocol,
        metadata_obj: CrfMetadata | RequisitionMetadata,
    ) -> None:
        self._source_model_obj = None
        self.metadata_obj = metadata_obj
        self.visit = visit

        # visit codes (and sequence) must match
        if (self.visit.visit_code != self.metadata_obj.visit_code) or (
            self.visit.visit_code_sequence != self.metadata_obj.visit_code_sequence
        ):
            raise MetadataWrapperError(
                f"Visit code mismatch. Visit is {self.visit.visit_code}."
                f"{self.visit.visit_code_sequence} but metadata object has "
                f"{self.metadata_obj.visit_code}."
                f"{self.metadata_obj.visit_code_sequence}. Got {metadata_obj!r}."
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.visit}, {self.metadata_obj})"

    @property
    def options(self) -> dict[str, Any]:
        """Returns a dictionary of query options."""
        return {f"{self.source_model_cls.related_visit_model_attr()}": self.visit}

    @property
    def source_model_obj(self) -> CrfModelMixin:
        if not self._source_model_obj:
            try:
                self._source_model_obj = self.source_model_cls.objects.get(**self.options)
            except AttributeError as e:
                if "related_visit_model_attr" not in str(e):
                    raise ImproperlyConfigured(f"{e} See {self.source_model_cls!r}")
            except ObjectDoesNotExist:
                self._source_model_obj = None
        return self._source_model_obj

    @source_model_obj.setter
    def source_model_obj(self, value=None) -> None:
        self._source_model_obj = value

    @property
    def source_model_cls(self) -> type[CrfModelMixin]:
        """Returns a CRF model class"""
        return django_apps.get_model(self.metadata_obj.model)
