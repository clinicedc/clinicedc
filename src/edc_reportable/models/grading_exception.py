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

    def grades(self) -> list[int]:
        grades = []
        for i in range(1, 5):
            if getattr(self, f"grade{i}"):
                grades.append(i)
        return grades

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Grading Exception"
        verbose_name_plural = "Grading Exceptions"
