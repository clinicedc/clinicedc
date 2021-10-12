from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..dosage_per_day import dosage_per_day
from .dosage_guideline import DosageGuideline
from .formulation import Formulation
from .list_models import FrequencyUnits
from .rx import Rx


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, prescription, medication, start_date):
        return self.get(prescription, medication, start_date)


class RxRefill(SiteModelMixin, edc_models.BaseUuidModel):

    rx = models.ForeignKey(Rx, on_delete=PROTECT)

    dosage_guideline = models.ForeignKey(DosageGuideline, on_delete=PROTECT)

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT, null=True)

    dose = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="dose per frequency if NOT considering weight",
    )

    calculate_dose = models.BooleanField(default=True)

    frequency = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
    )

    frequency_units = models.ForeignKey(
        FrequencyUnits,
        verbose_name="per",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    weight_in_kgs = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True
    )

    start_date = models.DateField(verbose_name="start", help_text="")

    end_date = models.DateField(verbose_name="end", help_text="inclusive")

    total = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate",
    )

    remaining = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate",
    )

    notes = models.TextField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Additional information for patient",
    )

    verified = models.BooleanField(default=False)

    verified_datetime = models.DateTimeField(null=True, blank=True)

    as_string = models.CharField(max_length=150, editable=False)

    on_site = CurrentSiteManager()

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return (
            f"{self.rx} "
            f"Take {self.dose} {self.formulation.formulation_type.display_name} {self.formulation.route.display_name} "
            # f"{self.frequency} {self.frequency_units.display_name}"
        )

    def natural_key(self):
        return (
            self.rx,
            self.medication,
            self.start_date,
        )

    def save(self, *args, **kwargs):
        if not kwargs.get("update_fields"):
            self.medication = self.dosage_guideline.medication
            # if not self.dose and self.calculate_dose:
            self.dose = dosage_per_day(
                self.dosage_guideline,
                weight_in_kgs=self.weight_in_kgs,
                strength=self.formulation.strength,
                strength_units=self.formulation.units.name,
            )
            self.frequency = self.dosage_guideline.frequency
            self.frequency_units = self.dosage_guideline.frequency_units
            self.total = float(self.dose) * float(self.rduration.days)
            self.as_string = str(self)
        super().save(*args, **kwargs)

    @property
    def subject_identifier(self):
        return self.rx.subject_identifier

    @property
    def rduration(self):
        return self.end_date - self.start_date

    @property
    def duration(self):
        display = str(self.rduration)
        return display.split(",")[0]

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "RX refill"
        verbose_name_plural = "RX refills"
        unique_together = ["rx", "dosage_guideline", "start_date"]
