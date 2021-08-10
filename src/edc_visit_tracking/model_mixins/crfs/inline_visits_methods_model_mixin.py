from django.db import models
from edc_crf.stubs import CrfModelStub


class InlineVisitMethodsModelMixin(models.Model):
    @property
    def visit_code(self: CrfModelStub):
        return self.subject_visit.visit_code

    @property
    def subject_identifier(self: CrfModelStub):
        return self.subject_visit.subject_identifier

    class Meta:
        abstract = True
