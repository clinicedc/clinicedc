from django.db import models
from edc_model.models import BaseUuidModel


class GradingException(BaseUuidModel):

    reference_range_collection = models.ForeignKey(
        "edc_reportable.ReferenceRangeCollection", on_delete=models.PROTECT
    )

    label = models.CharField(max_length=50)

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

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Grading Exception"
        verbose_name_plural = "Grading Exceptions"
