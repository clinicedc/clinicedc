from django.db import models

from edc_model.models import BaseUuidModel, HistoricalRecords


class MolecularWeight(BaseUuidModel):

    label = models.CharField(max_length=25, unique=True)

    mw = models.FloatField(verbose_name="Molecular weight", default=0, help_text="in g/mol")

    history = HistoricalRecords()

    def __str__(self):
        return self.label

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Molecular weight"
        verbose_name_plural = "Molecular weights"
