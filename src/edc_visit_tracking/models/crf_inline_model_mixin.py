from django.db import models


class CrfInlineModelMixin(models.Model):

    fk_model_attr = None

    def __unicode__(self):
        return str(self.fk_instance.get_visit())

    def __str__(self):
        return str(self.fk_instance.get_visit())

    def natural_key(self):
        return self.get_visit().natural_key()

    @property
    def fk_instance(self):
        """Return the instance of the inline parent model."""
        return getattr(self, self.fk_model_attr)

    @property
    def fk_model(self):
        """Return the class of the inline parent model."""
        return getattr(self.__class__, self.fk_model_attr).field.rel.to

    def get_visit(self):
        """Return the instance of the inline parent model's visit model."""
        return getattr(self.fk_instance, self.fk_model.visit_model_attr)

    def get_report_datetime(self):
        return self.get_visit().get_report_datetime()

    def get_subject_identifier(self):
        return self.get_visit().get_subject_identifier()

    class Meta:
        abstract = True
