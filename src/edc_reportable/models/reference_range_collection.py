from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_model.models import BaseUuidModel

from .grading_exception import GradingException


class ReferenceRangeCollection(BaseUuidModel):

    name = models.CharField(max_length=50, unique=True)

    grade1 = models.BooleanField(default=False)
    grade2 = models.BooleanField(default=False)
    grade3 = models.BooleanField(default=False)
    grade4 = models.BooleanField(default=False)

    grades = models.CharField(max_length=10, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        grades = []
        for i in range(1, 5):
            if getattr(self, f"grade{i}"):
                grades.append(str(i))
        self.grades = ",".join(grades)
        super().save(*args, **kwargs)

    def reportable_grades(self, label: str) -> list[str]:
        try:
            grading_exception = GradingException.objects.get(
                reference_range_collection=self, label=label
            )
        except ObjectDoesNotExist:
            reportable_grades = self.grades
        else:
            reportable_grades = grading_exception.grades
        return reportable_grades.split(",")

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Reference Range Collection"
        verbose_name_plural = "Reference Range Collections"
