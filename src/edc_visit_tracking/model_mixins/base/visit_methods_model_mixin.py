from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from ...exceptions import RelatedVisitFieldError
from ..utils import get_related_visit_model_attr
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

    natural_key.dependencies = [settings.SUBJECT_VISIT_MODEL]

    @classmethod
    def related_visit_model_attr(cls) -> str:
        """Returns the field name for the visit model foreign key."""
        return get_related_visit_model_attr(cls)

    @classmethod
    def related_visit_field_cls(cls) -> OneToOneField | None:
        """Returns the field class of the visit foreign key attribute."""
        related_visit_field_cls = None
        for fld_cls in cls._meta.get_fields():
            if fld_cls.name == cls.related_visit_model_attr():
                related_visit_field_cls = fld_cls
                break
        if not related_visit_field_cls:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_visit_field_cls

    @classmethod
    def related_visit_model_cls(cls) -> VisitModelMixin:
        """Returns the model class of the visit foreign key attribute."""
        related_model = None
        for fld_cls in cls._meta.get_fields():
            if fld_cls.name == cls.related_visit_model_attr():
                related_model = fld_cls.related_model
                break
        if not related_model:
            raise RelatedVisitFieldError(f"Related visit field class not found. See {cls}.")
        return related_model

    @classmethod
    def related_visit_model(cls) -> str:
        """Returns the name of the visit foreign key model in label_lower format"""
        return cls.related_visit_model_cls()._meta.label_lower

    @property
    def visit_code(self) -> str:
        return self.related_visit.visit_code

    @property
    def visit_code_sequence(self) -> int:
        return self.related_visit.visit_code_sequence

    @property
    def related_visit(self) -> VisitModelMixin:
        """Returns the model instance of the visit foreign key
        attribute.

        Note: doing this will cuase a RelatedObjectDoesNotExist exception:
            return getattr(self, self.related_visit_model_attr())
        RelatedObjectDoesNotExist cannot be imported since it is created
        at runtime.
        """
        related_visit = None
        for fld_cls in self._meta.get_fields():
            try:
                related_model = fld_cls.related_model
            except AttributeError:
                pass
            else:
                if related_model is not None and issubclass(related_model, (VisitModelMixin,)):
                    try:
                        related_visit = getattr(self, fld_cls.name)
                    except ObjectDoesNotExist:
                        pass
        return related_visit

    class Meta:
        abstract = True
