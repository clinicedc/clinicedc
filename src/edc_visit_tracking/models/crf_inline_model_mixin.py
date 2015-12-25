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
        return getattr(self, self.fk_attr)

    def get_visit(self):
        return getattr(self.fk_instance, self.fk_instance.visit_model_attr)

    def get_report_datetime(self):
        return self.get_visit().get_report_datetime()

    def get_subject_identifier(self):
        return self.get_visit().get_subject_identifier()

    class Meta:
        abstract = True
