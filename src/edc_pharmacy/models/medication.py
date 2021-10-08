from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models

from .list_models import Formulation, Route, Units


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, name, strength, units, formulation):
        return self.get(name, strength, units, formulation)


class Medication(edc_models.BaseUuidModel):

    name = models.CharField(max_length=35)

    strength = models.DecimalField(max_digits=6, decimal_places=1)

    units = models.ForeignKey(Units, on_delete=PROTECT)

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    route = models.ForeignKey(Route, on_delete=PROTECT)

    notes = models.TextField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return self.description

    def natural_key(self):
        return (
            self.name,
            self.strength,
            self.units,
            self.formulation,
        )

    @property
    def description(self):
        return (
            f"{self.name} {self.strength}{self.get_units_display()}. "
            f"{self.get_formulation_display()} "
            f"{self.get_route_display()}"
        )

    def get_formulation_display(self):
        return self.formulation.display_name

    def get_units_display(self):
        return self.units.display_name

    def get_route_display(self):
        return self.route.display_name

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication"
        verbose_name_plural = "Medications"
        unique_together = ["name", "strength", "units", "formulation"]
