from django.db import models


class MolecularWeight(models.Model):

    label = models.CharField(max_length=25, unique=True)

    mw = models.FloatField(verbose_name="Molecular weight", default=0, help_text="in g/mol")

    class Meta:
        verbose_name = "Molecular weight"
        verbose_name_plural = "Molecular weights"
