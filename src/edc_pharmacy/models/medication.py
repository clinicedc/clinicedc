from django.db import models
from edc_model import models as edc_models

from ..choices import DRUG_FORMULATION, DRUG_ROUTE, UNITS


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, name, strength, units, formulation):
        return self.get(name, strength, units, formulation)


class Medication(edc_models.BaseUuidModel):

    name = models.CharField(max_length=35)

    strength = models.DecimalField(max_digits=6, decimal_places=1)

    units = models.CharField(max_length=25, choices=UNITS)

    formulation = models.CharField(max_length=25, choices=DRUG_FORMULATION)

    route = models.CharField(max_length=25, choices=DRUG_ROUTE)

    notes = models.TextField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return (
            f"{self.name} {self.strength}{self.get_units_display()}. "
            f"{self.get_formulation_display()} "
            f"{self.get_route_display()}"
        )

    def natural_key(self):
        return (self.name, self.strength, self.units, self.formulation)

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication"
        verbose_name_plural = "Medications"
        unique_together = ["name", "strength", "units", "formulation"]
