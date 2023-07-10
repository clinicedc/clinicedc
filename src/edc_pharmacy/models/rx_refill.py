import math
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import convert_php_dateformat
from edc_utils.round_up import round_half_away_from_zero

from ..dosage_calculator import DosageCalculator
from ..model_mixins import MedicationOrderModelMixin, PreviousNextModelMixin
from .dosage_guideline import DosageGuideline
from .formulation import Formulation
from .rx import Rx


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, prescription, medication, refill_start_datetime):
        return self.get(prescription, medication, refill_start_datetime)


class RxRefill(
    PreviousNextModelMixin,
    MedicationOrderModelMixin,
    SiteModelMixin,
    edc_models.BaseUuidModel,
):
    rx = models.ForeignKey(Rx, on_delete=PROTECT)

    refill_identifier = models.CharField(max_length=36, default=uuid4, editable=False)

    dosage_guideline = models.ForeignKey(DosageGuideline, on_delete=PROTECT)

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT, null=True)

    dose = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="dose per frequency if NOT considering weight",
    )

    weight_in_kgs = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True, help_text="Defaults to 1.0"
    )

    refill_start_datetime = models.DateTimeField(
        verbose_name="Refill start date/time",
        # default=get_utcnow,
        help_text="Starting date for this refill",
    )

    refill_end_datetime = models.DateTimeField(
        verbose_name="Refill end date/time",
        null=True,
        help_text="Ending date for this refill",
    )

    number_of_days = models.IntegerField(null=True)

    roundup_dose = models.BooleanField(
        default=False, help_text="Rounds UP the dose. e.g. 7.3->8.0, 7.5->8.0"
    )

    round_dose = models.IntegerField(
        default=0, help_text="Rounds the dose. e.g. 7.3->7.0, 7.5->8.0"
    )

    roundup_divisible_by = models.IntegerField(
        default=0,
        help_text="Rounds up the total. For example, 32 would round 112 pills to 128 pills",
    )

    calculate_dose = models.BooleanField(default=True)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Total to be dispensed. Leave blank to auto-calculate",
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

    objects = Manager()

    on_site = CurrentSiteManager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        start_date = self.refill_start_datetime.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )
        end_date = self.refill_end_datetime.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )
        return (
            f"{self.rx} "
            f"Take {self.dose} {self.formulation.formulation_type.display_name} "
            f"{self.formulation.route.display_name}. "
            f"Valid: {start_date} to {end_date}."
        )

    def natural_key(self):
        return (self.refill_identifier,)  # noqa

    def save(self, *args, **kwargs):
        self.adjust_end_datetimes()
        self.number_of_days = (self.refill_end_datetime - self.refill_start_datetime).days
        if not self.weight_in_kgs:
            self.weight_in_kgs = self.rx.weight_in_kgs
        self.dose = Decimal(str(self.get_dose()))
        self.total = Decimal(str(self.get_total_to_dispense()))
        if not self.id:
            self.remaining = self.total
        self.as_string = str(self)
        super().save(*args, **kwargs)

    @property
    def frequency(self):
        return self.dosage_guideline.frequency

    @property
    def frequency_units(self):
        return self.dosage_guideline.frequency_units

    def get_dose(self) -> float:
        dosage = DosageCalculator(
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=self.weight_in_kgs,
        ).dosage
        if self.roundup_dose:
            return math.ceil(dosage)
        elif self.round_dose:
            return round_half_away_from_zero(dosage, self.round_dose)
        return dosage

    def get_total_to_dispense(self):
        """Returns total 'dispense unit (e.g.pills)' rounded up if
        divisor is greater than 1.
        """
        if self.roundup_divisible_by:
            return (
                math.ceil(
                    (
                        (
                            float(self.get_dose())
                            * float(self.frequency)
                            * float(self.number_of_days)
                        )
                        / self.roundup_divisible_by
                    )
                )
                * self.roundup_divisible_by
            )
        return float(self.get_dose()) * float(self.frequency) * float(self.number_of_days)

    @property
    def subject_identifier(self):
        return self.rx.subject_identifier

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "RX refill"
        verbose_name_plural = "RX refills"
        # unique_together = (("rx", "refill_start_datetime"),)
