from django.db import models

from .visit_model_mixin import VisitModelMixin


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to the visit tracking model."""

    def contribute_to_class(self, model, name):
        super(CrfModelManager, self).contribute_to_class(model, name)
        model.visit_model, model.visit_model_attr = self._configure_visit_model_attrs(model)
        try:
            model.get_visit = lambda self: getattr(self, model.visit_model_attr)
        except TypeError as e:
            raise TypeError(e, 'Specify the visit_model_attr on {}'.format(model))

    """Manager for all scheduled models (those with a maternal_visit fk)."""
    def get_by_natural_key(self, report_datetime, visit_instance_number, code, subject_identifier_as_pk):
        instance = self.model.visit_model.objects.get_by_natural_key(
            report_datetime, visit_instance_number, code, subject_identifier_as_pk)
        return self.get({self.model.visit_model_attr: instance})

    def _configure_visit_model_attrs(self, model):
        """Sets visit_model and visit_model_attr on the model class."""
        visit_model, visit_model_attr = None, None
        for field in model._meta.fields:
            try:
                if issubclass(field.rel.to, VisitModelMixin):
                    visit_model = field.rel.to
                    visit_model_attr = field.name
                    break
            except AttributeError:
                pass
        try:
            if model.visit_model_attr:
                visit_model_attr = model.visit_model_attr
        except AttributeError:
            pass
        return visit_model, visit_model_attr
