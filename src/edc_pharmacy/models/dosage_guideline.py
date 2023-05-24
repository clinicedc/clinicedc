from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models
from edc_utils.round_up import round_half_away_from_zero

from .list_models import FrequencyUnits, Units
from .medication import Medication


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, medication_name, dose, dose_units, dose_per_kg):
        return self.get(medication_name, dose, dose_units, dose_per_kg)


class DosageGuideline(edc_models.BaseUuidModel):

    """Dosage guidelines."""

    medication = models.ForeignKey(Medication, on_delete=PROTECT, null=True, blank=False)

    dose = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="dose per 'frequency unit' if NOT considering subject's weight",
    )

    dose_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="dose per 'frequency unit' if considering subject's weight",
    )

    dose_units = models.ForeignKey(Units, on_delete=PROTECT)

    frequency = models.DecimalField(
        verbose_name="Frequency",
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1.0)],
        default=1,
        help_text="number of times per 'frequency unit'",
    )

    frequency_units = models.ForeignKey(
        FrequencyUnits,
        verbose_name="Frequency unit",
        on_delete=PROTECT,
    )

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return (
            f"{self.medication.name} {round_half_away_from_zero(self.dose or 0, 0)}"
            f"{self.dose_units} {round_half_away_from_zero((self.frequency or 0), 0)} "
            f"{self.get_frequency_units_display()}{' (per kg)' if self.dose_per_kg else ''}"
        )

    def natural_key(self):
        return (
            self.medication,
            self.dose,
            self.dose_units,
            self.dose_per_kg,
        )

    def get_dose_units_display(self):
        return self.dose_units.display_name

    def get_frequency_units_display(self):
        return self.frequency_units.display_name

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Dosage Guideline"
        verbose_name_plural = "Dosage Guidelines"
        unique_together = [
            ["medication", "dose", "dose_units", "dose_per_kg"],
        ]
