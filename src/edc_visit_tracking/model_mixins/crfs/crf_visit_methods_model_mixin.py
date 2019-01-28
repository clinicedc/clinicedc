from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from ..visit_model_mixin import VisitModelMixin


class CrfVisitMethodsModelMixin(models.Model):
    @property
    def visit_code(self):
        return self.visit.visit_code

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier

    @property
    def visit(self):
        """Returns the model instance of the visit foreign key
        attribute.
        """
        visit = None
        fields = {field.name: field for field in self._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin,)):
                    try:
                        visit = getattr(self, name)
                    except ObjectDoesNotExist:
                        pass
        return visit

    @classmethod
    def visit_model_attr(cls):
        """Returns the field name for the visit model
        foreign key.
        """
        visit_model_attr = None
        fields = {field.name: field for field in cls._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin,)):
                    visit_model_attr = name
        return visit_model_attr

    @classmethod
    def visit_model(cls):
        """Returns the visit foreign key model in
        label_lower format.
        """
        return cls.visit_model_cls()._meta.label_lower

    @classmethod
    def visit_model_cls(cls):
        """Returns the visit foreign key attribute model class.
        """
        visit_model_cls = None
        fields = {field.name: field for field in cls._meta.fields}
        for field in fields.values():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin,)):
                    visit_model_cls = field.related_model
        return visit_model_cls

    class Meta:
        abstract = True
