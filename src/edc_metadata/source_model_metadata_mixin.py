from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from edc_visit_tracking.typing_stubs import RelatedVisitProtocol


class SourceModelMetadataMixin:
    """Mixin class for Metadata and MetadataUpdater class."""

    def __init__(self, source_model: str, related_visit: RelatedVisitProtocol = None):
        self._source_model_obj = None
        self._source_model = source_model
        self.related_visit = related_visit

    @property
    def source_model(self) -> str:
        return self._source_model

    @property
    def source_model_cls(self):
        return django_apps.get_model(self.source_model)

    @property
    def source_model_obj(self):
        if not self._source_model_obj:
            try:
                self._source_model_obj = self.source_model_cls.objects.get(
                    subject_visit=self.related_visit
                )
            except ObjectDoesNotExist:
                self._source_model_obj = None
        return self._source_model_obj

    @property
    def is_keyed(self) -> bool:
        """Returns True if source model exists."""
        if self.source_model_obj:
            return True
        return False

    @property
    def due_datetime(self):
        return self.related_visit.report_datetime

    @property
    def fill_datetime(self):
        if self.source_model_obj:
            return self.source_model_obj.created
        return None

    @property
    def document_user(self):
        if self.source_model_obj:
            document_user = self.source_model_obj.user_created
        else:
            document_user = self.related_visit.user_created
        return document_user

    @property
    def document_name(self):
        return self.source_model_cls._meta.verbose_name
