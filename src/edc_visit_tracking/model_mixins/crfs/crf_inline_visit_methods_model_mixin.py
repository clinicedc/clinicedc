from django.db import models


class CrfInlineVisitMethodsModelMixin(models.Model):
    @property
    def visit_code(self):
        return self.visit.visit_code

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier

    class Meta:
        abstract = True
