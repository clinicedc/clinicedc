from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import options, OneToOneField, ForeignKey

from .crf_inline_visit_methods_model_mixin import CrfInlineVisitMethodsModelMixin


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("crf_inline_parent",)


class CrfInlineModelMixin(CrfInlineVisitMethodsModelMixin, models.Model):
    """A mixin for models used as inlines in ModelAdmin.
    """

    def __init__(self, *args, **kwargs):
        """Try to detect the inline parent model attribute
        name or raise.
        """
        super().__init__(*args, **kwargs)
        try:
            self._meta.crf_inline_parent
        except AttributeError:
            fks = [
                field
                for field in self._meta.fields
                if isinstance(field, (OneToOneField, ForeignKey))
            ]
            if len(fks) == 1:
                self.__class__._meta.crf_inline_parent = fks[0].name
            else:
                raise ImproperlyConfigured(
                    "CrfInlineModelMixin cannot determine the "
                    "inline parent model name. Got more than one foreign key. "
                    "Try declaring \"crf_inline_parent = '<field name>'\" "
                    "explicitly in Meta."
                )

    def __str__(self):
        return str(self.parent_instance.visit)

    def natural_key(self):
        return self.visit.natural_key()

    @property
    def parent_instance(self):
        """Return the instance of the inline parent model.
        """
        return getattr(self, self._meta.crf_inline_parent)

    @property
    def parent_model(self):
        """Return the class of the inline parent model.
        """
        field = getattr(self.__class__, self._meta.crf_inline_parent).field
        try:
            return field.rel.to
        except AttributeError:
            return field.remote_field.model  # django 2.0 +

    @property
    def visit(self):
        """Return the instance of the inline parent model's visit
        model.
        """
        return getattr(self.parent_instance, self.parent_model.visit_model_attr())

    @property
    def report_datetime(self):
        """Return the instance of the inline parent model's
        report_datetime.
        """
        return self.visit.report_datetime

    class Meta:
        crf_inline_parent = None
        abstract = True
