from django.db import models
import django.db.models.options as options
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.core.exceptions import ImproperlyConfigured

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('crf_inline_parent_model',)


class CrfInlineModelMixin(models.Model):
    """A mixin for models used as inlines in ModelAdmin."""

    def __init__(self, *args, **kwargs):
        """Try to detect the inline parent model attribute name or raise,"""
        super(CrfInlineModelMixin, self).__init__(*args, **kwargs)
        try:
            self._meta.crf_inline_parent_model
        except AttributeError:
            fks = [field for field in self._meta.fields if isinstance(field, (OneToOneField, ForeignKey))]
            if len(fks) == 1:
                self.__class__._meta.crf_inline_parent_model = fks[0].name
            else:
                raise ImproperlyConfigured(
                    'CrfInlineModelMixin cannot determine the inline parent model name. '
                    'Got more than one foreign key. Try declaring \"crf_inline_parent_model = \'<field name>\'\" '
                    'explicitly in Meta.')

    def __str__(self):
        return str(self.parent_instance.get_visit())

    def natural_key(self):
        return self.get_visit().natural_key()

    @property
    def parent_instance(self):
        """Return the instance of the inline parent model."""
        return getattr(self, self._meta.crf_inline_parent_model)

    @property
    def parent_model(self):
        """Return the class of the inline parent model."""
        return getattr(self.__class__, self._meta.crf_inline_parent_model).field.rel.to

    def get_visit(self):
        """Return the instance of the inline parent model's visit model."""
        return getattr(self.parent_instance, self.parent_model.visit_model_attr)

    def get_report_datetime(self):
        return self.get_visit().get_report_datetime()

    def get_subject_identifier(self):
        return self.get_visit().get_subject_identifier()

    class Meta:
        crf_inline_parent_model = None  # foreign key attribute that relates this model to the parent model
        abstract = True
