from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models
from edc_utils.round_up import round_half_away_from_zero

from .list_models import FormulationType, Route, Units
from .medication import Medication


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name, strength, units, formulation_type):
        return self.get(name, strength, units, formulation_type)


class Formulation(edc_models.BaseUuidModel):
    medication = models.ForeignKey(Medication, on_delete=PROTECT, null=True, blank=False)

    strength = models.DecimalField(max_digits=6, decimal_places=1)

    units = models.ForeignKey(Units, on_delete=PROTECT)

    formulation_type = models.ForeignKey(FormulationType, on_delete=PROTECT)

    route = models.ForeignKey(Route, on_delete=PROTECT)

    notes = models.TextField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return self.description.title()

    def natural_key(self):
        return (
            self.medication,
            self.strength,
            self.units,
            self.formulation_type,
        )

    @property
    def description(self):
        return (
            f"{self.medication} {round_half_away_from_zero(self.strength, 0)}"
            f"{self.get_units_display()} "
            f"{self.get_formulation_type_display()} "
            f"{self.get_route_display()}"
        )

    def get_formulation_type_display(self):
        return self.formulation_type.display_name

    def get_units_display(self):
        return self.units.display_name

    def get_route_display(self):
        return self.route.display_name

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Formulation"
        verbose_name_plural = "Formulations"
        unique_together = ["medication", "strength", "units", "formulation_type"]
