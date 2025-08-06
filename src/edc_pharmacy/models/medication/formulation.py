from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import PROTECT, UniqueConstraint
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils.round_up import round_half_away_from_zero

from .formulation_type import FormulationType
from .medication import Medication
from .route import Route
from .units import Units

if TYPE_CHECKING:
    from ..medication import Assignment


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name, strength, units, formulation_type):
        return self.get(name, strength, units, formulation_type)


class Formulation(BaseUuidModel):

    medication = models.ForeignKey(Medication, on_delete=PROTECT, null=True, blank=False)

    strength = models.DecimalField(max_digits=6, decimal_places=1)

    units = models.ForeignKey(Units, on_delete=PROTECT)

    formulation_type = models.ForeignKey(FormulationType, on_delete=PROTECT)

    route = models.ForeignKey(Route, on_delete=PROTECT)

    notes = models.TextField(max_length=250, null=True, blank=True)

    description = models.CharField(max_length=250, null=True, blank=True)

    imp = models.BooleanField(default=False)

    imp_description = models.CharField(max_length=250, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.description

    def natural_key(self):
        return (
            self.medication,
            self.strength,
            self.units,
            self.formulation_type,
        )

    def save(self, *args, **kwargs):
        self.description = self.get_description()
        if not self.imp:
            self.imp_description = None
        else:
            self.imp_description = (
                self.imp_description if self.imp_description else self.description
            )
        super().save(*args, **kwargs)

    def get_description(self):
        return (
            f"{self.medication} {round_half_away_from_zero(self.strength, 0)}"
            f"{self.get_units_display()} "
            # f"{self.get_formulation_type_display()} "
            f"{self.get_route_display()}"
        )

    def get_product_description(self):
        return (
            f"{self.medication} {round_half_away_from_zero(self.strength, 0)}"
            f"{self.get_units_display()} "
            # f"{self.get_formulation_type_display()} "
        )

    def get_description_with_assignment(self, assignment: Assignment) -> str:
        description = self.description
        return (
            f"{self.medication.display_name.title()} "
            f"{assignment.display_name.upper()} "
            f"{description.split(str(self.medication))[1]}"
        )

    def get_formulation_type_display(self):
        return self.formulation_type.display_name

    def get_units_display(self):
        return self.units.display_name

    def get_route_display(self):
        return self.route.display_name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Formulation"
        verbose_name_plural = "Formulations"
        constraints = [
            UniqueConstraint(
                fields=["medication", "strength", "units", "formulation_type"],
                name="%(app_label)s_%(class)s_med_stren_uniq",
            )
        ]
