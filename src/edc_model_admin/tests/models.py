from django.db import models
from edc_model.models import BaseUuidModel
from edc_visit_schedule.visit.visit import Visit
from dateutil.relativedelta import relativedelta
from django.db.models.deletion import CASCADE


class BasicModel(BaseUuidModel):

    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    f3 = models.CharField(max_length=10, null=True, blank=False)
    f4 = models.CharField(max_length=10, null=True, blank=False)
    f5 = models.CharField(max_length=10)
    f5_other = models.CharField(max_length=10, null=True)
    subject_identifier = models.CharField(max_length=25, default="12345")


class SubjectVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    @property
    def appointment(self):
        pass

    @property
    def visit(self):
        return Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )


class CrfModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=CASCADE)

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr())

    @classmethod
    def visit_model_attr(cls):
        return "subject_visit"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.subject_visit.subject_identifier
        super().save(*args, **kwargs)


class RequisitionModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=CASCADE)

    panel_name = models.CharField(max_length=25)

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr())

    @classmethod
    def visit_model_attr(cls):
        return "subject_visit"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.subject_visit.subject_identifier
        super().save(*args, **kwargs)
