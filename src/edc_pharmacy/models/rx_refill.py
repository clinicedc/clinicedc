from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow_as_date
from edc_visit_schedule.model_mixins import VisitCodeFieldsModelMixin

from ..dosage_per_day import dosage_per_day
from ..exceptions import ActivePrescriptionRefillExists
from .dosage_guideline import DosageGuideline
from .formulation import Formulation
from .list_models import FrequencyUnits
from .model_mixins import MedicationOrderModelMixin
from .rx import Rx


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, prescription, medication, refill_date):
        return self.get(prescription, medication, refill_date)


class RxRefill(
    MedicationOrderModelMixin,
    VisitCodeFieldsModelMixin,
    SiteModelMixin,
    edc_models.BaseUuidModel,
):

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

    refill_date = models.DateField(
        verbose_name="Refill date", default=get_utcnow_as_date, help_text=""
    )

    number_of_days = models.IntegerField(null=True)

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

    active = models.BooleanField(default=False)

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
            self.refill_date,
        )

    def save(self, *args, **kwargs):
        if self.active:
            # TODO: does this matter?
            opts = dict(id=self.id) if self.id else {}
            if (
                self.__class__.objects.filter(
                    rx__subject_identifier=self.rx.subject_identifier,
                    dosage_guideline=self.dosage_guideline,
                    active=True,
                )
                .exclude(**opts)
                .exists()
            ):
                raise ActivePrescriptionRefillExists(
                    f"Unable to save as an active refill. An active refill already exists."
                )

        self.medication = self.dosage_guideline.medication
        # if not self.dose and self.calculate_dose:
        self.frequency = self.dosage_guideline.frequency
        self.frequency_units = self.dosage_guideline.frequency_units
        self.dose = self.get_dose()
        self.total = self.get_total()
        if not self.id:
            self.remaining = self.total
        self.as_string = str(self)
        super().save(*args, **kwargs)

    def get_dose(self):
        return dosage_per_day(
            self.dosage_guideline,
            weight_in_kgs=self.weight_in_kgs,
            strength=self.formulation.strength,
            strength_units=self.formulation.units.name,
        )

    def get_total(self):
        return float(self.dose) * float(self.number_of_days)

    @property
    def subject_identifier(self):
        return self.rx.subject_identifier

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "RX refill"
        verbose_name_plural = "RX refills"
        unique_together = [
            ["rx", "dosage_guideline", "refill_date"],
            ["rx", "visit_code", "visit_code_sequence"],
        ]
