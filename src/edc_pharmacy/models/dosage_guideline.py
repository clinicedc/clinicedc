from django.core.validators import MinValueValidator
from django.db import models
from edc_base.model_mixins import BaseUuidModel

from ..choices import UNITS, FREQUENCY
from ..dosage_calculator import DosageCalculator


class DosageGuideline(BaseUuidModel):

    """Dosage guidelines.
    """

    dose_calculator_cls = DosageCalculator

    medication_name = models.CharField(max_length=25)

    dose = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='dose per frequency if NOT considering weight')

    dose_per_kg = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='dose per frequency if considering weight')

    dose_units = models.CharField(
        max_length=25,
        choices=UNITS)

    dose_frequency_factor = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(1.0)],
        default=1)

    dose_frequency_units = models.CharField(
        verbose_name='per',
        max_length=10,
        choices=FREQUENCY,
        default='day')

    subject_weight_factor = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=1,
        help_text='factor to convert weight to kg')

    def __str__(self):
        if self.dose_per_kg:
            return (f'{self.medication_name} {self.dose_per_kg}{self.dose_units}'
                    f'/per kg/{self.get_dose_frequency_units_display()}')
        else:
            return (f'{self.medication_name} {self.dose}{self.dose_units}/'
                    f'{self.get_dose_frequency_units_display()}')

    @property
    def dosage_per_kg_per_day(self):
        """Returns a decimal value or raises an exception.
        """
        return self.dose_calculator_cls(**self.__dict__).dosage_per_kg_per_day

    def dosage_per_day(self, **kwargs):
        """Returns a decimal value or raises an exception.
        """
        return self.dose_calculator_cls(**self.__dict__).dosage_per_day(**kwargs)

    class Meta:
        unique_together = ['medication_name', 'dose_units']
