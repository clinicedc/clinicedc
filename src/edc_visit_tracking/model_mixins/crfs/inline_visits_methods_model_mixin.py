from django.db import models


class InlineVisitMethodsModelMixin(models.Model):
    @property
    def visit_code(self):
        return self.subject_visit.visit_code

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier

    class Meta:
        abstract = True
