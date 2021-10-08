from django.core.validators import MinValueValidator
from django.db import models
from edc_model import models as edc_models

from ..choices import FREQUENCY, UNITS
from ..dosage_calculator import DosageCalculator


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, medication_name, dose, dose_units, dose_per_kg):
        return self.get(medication_name, dose, dose_units, dose_per_kg)


class DosageGuideline(edc_models.BaseUuidModel):

    """Dosage guidelines."""

    dose_calculator_cls = DosageCalculator

    medication_name = models.CharField(max_length=25)

    dose = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="dose per frequency if NOT considering weight",
    )

    dose_per_kg = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="dose per frequency if considering weight",
    )

    dose_units = models.CharField(max_length=25, choices=UNITS)

    dose_frequency_factor = models.DecimalField(
        max_digits=6, decimal_places=1, validators=[MinValueValidator(1.0)], default=1
    )

    dose_frequency_units = models.CharField(
        verbose_name="per", max_length=10, choices=FREQUENCY, default="day"
    )

    subject_weight_factor = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=1,
        help_text="factor to convert weight to kg",
    )

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        if self.dose_per_kg:
            return (
                f"{self.medication_name} {self.dose_per_kg}{self.dose_units}"
                f"/per kg/{self.get_dose_frequency_units_display()}"
            )
        else:
            return (
                f"{self.medication_name} {self.dose}{self.dose_units}/"
                f"{self.get_dose_frequency_units_display()}"
            )

    def natural_key(self):
        return (self.medication_name, self.dose, self.dose_units, self.dose_per_kg)

    @property
    def dosage_per_kg_per_day(self):
        """Returns a decimal value or raises an exception."""
        return self.dose_calculator_cls(**self.__dict__).dosage_per_kg_per_day

    def dosage_per_day(self, **kwargs):
        """Returns a decimal value or raises an exception."""
        return self.dose_calculator_cls(**self.__dict__).dosage_per_day(**kwargs)

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Dosage Guideline"
        verbose_name_plural = "Dosage Guidelines"
        unique_together = ["medication_name", "dose", "dose_units", "dose_per_kg"]
