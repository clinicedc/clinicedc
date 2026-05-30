from django.db import models

from edc_model.models import BaseUuidModel


class InvestigationMapping(BaseUuidModel):
    laboratory = models.CharField(
        verbose_name="Laboratory",
        max_length=100,
    )

    investigation = models.CharField(
        verbose_name="Investigation name (from PDF)",
        max_length=50,
    )

    utest_id = models.CharField(
        verbose_name="EDC utest_id",
        max_length=25,
        blank=True,
        default="",
        help_text="Blank if no EDC equivalent exists yet.",
    )

    in_reportable = models.BooleanField(
        verbose_name="In reportable normal data",
        default=False,
        help_text="True if the utest_id exists in edc_reportable NormalData.",
    )

    def __str__(self):
        return f"{self.laboratory} {self.investigation}->{self.utest_id}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Investigation Mapping"
        verbose_name_plural = "Investigation Mappings"
        constraints = (
            models.UniqueConstraint(
                fields=["laboratory", "investigation"],
                name="unique_lab_investigation",
            ),
        )
