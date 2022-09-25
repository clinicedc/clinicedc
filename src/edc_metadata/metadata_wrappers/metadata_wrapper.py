from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin

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
        visit: VisitModelMixin,
        metadata_obj: CrfMetadata | RequisitionMetadata,
    ) -> None:
        self._model_obj = None
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
                f"{self.metadata_obj.visit_code_sequence}. Got {repr(metadata_obj)}."
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.visit}, {self.metadata_obj})"

    @property
    def options(self) -> dict:
        """Returns a dictionary of query options."""
        return {f"{self.model_cls.related_visit_model_attr()}": self.visit}

    @property
    def model_obj(self) -> CrfModelMixin:
        if not self._model_obj:
            try:
                self._model_obj = self.model_cls.objects.get(**self.options)
            except AttributeError as e:
                if "related_visit_model_attr" not in str(e):
                    raise ImproperlyConfigured(f"{e} See {repr(self.model_cls)}")
            except ObjectDoesNotExist:
                self._model_obj = None
        return self._model_obj

    @model_obj.setter
    def model_obj(self, value=None) -> None:
        self._model_obj = value

    @property
    def model_cls(self) -> CrfModelMixin:
        """Returns a CRF model class"""
        return django_apps.get_model(self.metadata_obj.model)
