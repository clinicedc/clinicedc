from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from datetime import datetime

    from edc_crf.model_mixins import CrfModelMixin
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..model_mixins.creates import CreatesMetadataModelMixin

    class RelatedVisitModel(SiteModelMixin, CreatesMetadataModelMixin, Base, BaseUuidModel):
        pass


class SourceModelMetadataMixin:
    """Mixin class for Metadata and MetadataUpdater class."""

    def __init__(self, source_model: str, related_visit: RelatedVisitModel = None):
        self._source_model_obj = None
        self._source_model = source_model
        self.related_visit = related_visit

    @property
    def source_model(self) -> str:
        return self._source_model

    @property
    def source_model_cls(self) -> type[CrfModelMixin]:
        return django_apps.get_model(self.source_model)

    @property
    def source_model_obj(self) -> CrfModelMixin | None:
        """Returns the source model instance or None."""
        if not self._source_model_obj:
            try:
                self._source_model_obj = self.source_model_cls.objects.get(
                    **self.source_model_options
                )
            except ObjectDoesNotExist:
                self._source_model_obj = None
        return self._source_model_obj

    @property
    def source_model_options(self) -> dict[str, Any]:
        """Returns a dictionary of query options to get/filter the
        source_obj.
        """
        return dict(subject_visit_id=self.related_visit.id)

    @property
    def source_model_obj_exists(self) -> bool:
        """Returns True if the source model instance exists."""
        return self.source_model_cls.objects.filter(**self.source_model_options).exists()

    @property
    def due_datetime(self) -> datetime | None:
        return self.related_visit.report_datetime

    @property
    def fill_datetime(self) -> datetime | None:
        return getattr(self.source_model_obj, "created", None)

    @property
    def document_user(self) -> str | None:
        return getattr(self.source_model_obj, "user_created", self.related_visit.user_created)

    @property
    def document_name(self) -> str | None:
        return self.source_model_cls._meta.verbose_name
