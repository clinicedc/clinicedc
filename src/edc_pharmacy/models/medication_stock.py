from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models

from .list_models import Container
from .medication import Medication


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, container, count_per_container, *args):
        Medication.objects.get(*args)
        return self.get(name, strength, units, formulation)


class MedicationStock(edc_models.BaseUuidModel):

    medication = models.ForeignKey(Medication, on_delete=PROTECT)

    container = models.ForeignKey(Container, on_delete=PROTECT)

    count_per_container = models.DecimalField(max_digits=6, decimal_places=1)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return (
            f"{self.medication.description}. "
            f"{self.container} of "
            f"{self.count_per_container} {self.medication.get_formulation_display()}"
        )

    def natural_key(self):
        return (
            (self.count_per_container,)
            + self.container.natural_key()
            + self.medication.natural_key()
        )

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication stock"
        verbose_name_plural = "Medication stock"
        unique_together = ["medication__id", "container", "count_per_container"]
