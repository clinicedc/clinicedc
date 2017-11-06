from django.db import models
from edc_base.model_mixins import BaseUuidModel

from ..choices import DRUG_FORMULATION, DRUG_ROUTE, UNITS


class Medication(BaseUuidModel):

    name = models.CharField(
        max_length=35)

    strength = models.DecimalField(
        max_digits=6,
        decimal_places=1)

    units = models.CharField(
        max_length=25,
        choices=UNITS)

    formulation = models.CharField(
        max_length=25,
        choices=DRUG_FORMULATION)

    route = models.CharField(
        max_length=25,
        choices=DRUG_ROUTE)

    notes = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    def __str__(self):
        return (f'{self.name} {self.strength}{self.get_units_display()}. '
                f'{self.get_formulation_display()} '
                f'{self.get_route_display()}')

    class Meta:
        unique_together = ['name', 'strength', 'units', 'formulation']
        verbose_name_plural = 'Medication'
