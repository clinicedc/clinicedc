from django.db import models


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to the visit tracking model."""

    def get_by_natural_key(self, visit_instance_number, code, subject_identifier_as_pk):
        instance = self.model.visit_model.objects.get_by_natural_key(
            visit_instance_number, code, subject_identifier_as_pk)
        return self.get({self.model.visit_model_attr(): instance})

    def get_for_visit(self, visit, **kwargs):
        """Returns an instance for the given visit."""
        options = {self.model.visit_model_attr(): visit}
        options.update(**kwargs)
        return self.get(**options)

    def get_for_subject_identifier(self, subject_identifier):
        """Returns a queryset for the given subject_identifier."""
        options = {'{}__subject_identifier'.format(self.model.visit_model_attr()): subject_identifier}
        return self.filter(**options)


class VisitModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier, visit_schedule_name, schedule_name, visit_code):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code)
