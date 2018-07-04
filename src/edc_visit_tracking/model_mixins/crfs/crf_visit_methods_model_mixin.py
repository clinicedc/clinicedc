from django.db import models

from ..visit_model_mixin import VisitModelMixin
from django.core.exceptions import ObjectDoesNotExist


class CrfVisitMethodsModelMixin(models.Model):

    @property
    def visit_code(self):
        return self.visit.visit_code

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier

    @property
    def visit(self):
        """Returns the visit foreign key attribute value
        from this instance.
        """
        visit = None
        fields = {field.name: field for field in self._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin, )):
                    try:
                        visit = getattr(self, name)
                    except ObjectDoesNotExist:
                        pass
        return visit

    @classmethod
    def visit_model_attr(cls):
        """Returns the field attribute name for the visit model
        foreign key.
        """
        visit_model_attr = None
        fields = {
            field.name: field for field in cls._meta.fields}
        for name, field in fields.items():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin, )):
                    visit_model_attr = name
        return visit_model_attr

    @classmethod
    def visit_model(cls):
        """Returns the visit model foreign key in
        label_lower format.
        """
        return cls.visit_model_cls()._meta.label_lower

    @classmethod
    def visit_model_cls(cls):
        """Returns the visit model class for the visit
        foreign key attribute from this model class.
        """
        visit_model_cls = None
        fields = {field.name: field for field in cls._meta.fields}
        for field in fields.values():
            try:
                assert field.related_model is not None
            except (AttributeError, AssertionError):
                pass
            else:
                if issubclass(field.related_model, (VisitModelMixin, )):
                    visit_model_cls = field.related_model
        return visit_model_cls

#     @classmethod
#     def visit_model_attr(cls):
#         """Returns the field attribute name that refers to
#         the visit model FK, e.g. "subject_visit".
#         """
#         app_config = django_apps.get_app_config('edc_visit_tracking')
#         return app_config.visit_model_attr(cls._meta.label_lower)
#
#     @classmethod
#     def visit_model(cls):
#         """Returns the visit model in label lower format,
#         e.g. myapplabel_subjectvisit.
#         """
#         app_config = django_apps.get_app_config('edc_visit_tracking')
#         return app_config.visit_model(cls._meta.app_label)
#
#     @property
#     def visit(self):
#         """Returns the visit model FK instance.
#         """
#         return getattr(self, self.visit_model_attr())

    class Meta:
        abstract = True
