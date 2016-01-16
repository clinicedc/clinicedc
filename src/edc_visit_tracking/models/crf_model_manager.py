from django.db import models


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to the visit tracking model."""

    def get_by_natural_key(self, visit_instance_number, code, subject_identifier_as_pk):
        instance = self.model.visit_model.objects.get_by_natural_key(
            visit_instance_number, code, subject_identifier_as_pk)
        return self.get({self.model.visit_model_attr: instance})
