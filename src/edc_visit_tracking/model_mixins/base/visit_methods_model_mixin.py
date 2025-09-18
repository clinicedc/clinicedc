from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.admin.utils import NotRelationField, get_model_from_relation
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import models

from ...exceptions import RelatedVisitFieldError
from ..visit_model_mixin import VisitModelMixin

if TYPE_CHECKING:
    from django.db.models import OneToOneField


class VisitMethodsModelMixin(models.Model):
    """A model mixin for CRFs and Requisitions to add methods to
    access the related visit model and its attributes.

    Used by VisitTrackingCrfModelMixin.
    """

    def __str__(self) -> str:
        return str(self.related_visit)

    def natural_key(self) -> tuple:
        return tuple(getattr(self, self.related_visit_model_attr()).natural_key())

    natural_key.dependencies = (settings.SUBJECT_VISIT_MODEL,)

    @classmethod
    def related_visit_model_attr(cls) -> str:
        """Returns the field name for the related visit model
        foreign key.
        """
        return cls.related_visit_field_cls().name
        # return get_related_visit_model_attr(cls)

    @classmethod
    def related_visit_field_cls(cls) -> OneToOneField | None:
        """Returns the 'field' class of the related visit foreign
        key attribute.
        """
        related_visit_field_cls = None
        for field in cls._meta.get_fields():
            try:
                related_model = get_model_from_relation(field)
            except NotRelationField:
                continue
            else:
                if issubclass(related_model, (VisitModelMixin,)):
                    related_visit_field_cls = field
                    break
        if not related_visit_field_cls:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_visit_field_cls

    @classmethod
    def related_visit_model_cls(cls) -> type[VisitModelMixin]:
        """Returns the 'model' class of the related visit foreign
        key attribute.
        """
        related_model = None
        for field in cls._meta.get_fields():
            try:
                related_model = get_model_from_relation(field)
            except NotRelationField:
                continue
            else:
                if issubclass(related_model, (VisitModelMixin,)):
                    break
        if not related_model:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_model

    @classmethod
    def related_visit_model(cls) -> str:
        """Returns the name of the related_visit FK model in
        label_lower format.
        """
        return cls.related_visit_model_cls()._meta.label_lower

    @property
    def visit_code(self) -> str:
        return self.related_visit.visit_code

    @property
    def visit_code_sequence(self) -> int:
        return self.related_visit.visit_code_sequence

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns the instance of the related_visit FK."""
        related_model = None
        related_visit = None
        for field in self._meta.get_fields():
            try:
                related_model = get_model_from_relation(field)
            except NotRelationField:
                continue
            else:
                if issubclass(related_model, (VisitModelMixin,)):
                    try:
                        related_visit = getattr(self, field.name)
                    except ObjectDoesNotExist as e:
                        raise RelatedVisitFieldError(
                            f"Related visit cannot be None. See {self.__class__}. "
                            "Perhaps catch this in the form."
                        ) from e
                    break
                related_model = None
        if not related_model:
            raise ImproperlyConfigured(
                f"Model is missing a FK to a related visit model. See {self.__class__}."
            )
        return related_visit

    class Meta:
        abstract = True
