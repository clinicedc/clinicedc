from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.deletion import PROTECT
from edc_base.model_mixins.base_uuid_model import BaseUuidModel

from ..choices import TIMING
from .dosage_guideline import DosageGuideline
from .medication import Medication
from .prescription import Prescription


class PrescriptionItem(BaseUuidModel):

    prescription = models.ForeignKey(Prescription, on_delete=PROTECT)

    medication = models.ForeignKey(Medication, on_delete=PROTECT)

    dosage_guideline = models.ForeignKey(DosageGuideline, on_delete=PROTECT)

    dose = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Leave blank to auto-calculate')

    calculate_dose = models.BooleanField(default=True)

    frequency = models.IntegerField(
        validators=[MinValueValidator(1)])

    frequency_units = models.CharField(
        verbose_name='per',
        max_length=10,
        default='day',
        choices=TIMING)

    start_date = models.DateField(
        verbose_name='start',
        help_text='')

    end_date = models.DateField(
        verbose_name='end',
        help_text='inclusive')

    total = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Leave blank to auto-calculate')

    remaining = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Leave blank to auto-calculate')

    notes = models.TextField(
        max_length=250,
        null=True,
        blank=True,
        help_text='Additional information for patient')

    verified = models.BooleanField(default=False)

    verified_datetime = models.DateTimeField(null=True, blank=True)

    as_string = models.CharField(max_length=150, editable=False)

    def __str__(self):
        return (f'{str(self.medication)} * {self.dose} '
                f'{self.medication.get_formulation_display()}(s) '
                f'{self.frequency} {self.get_frequency_units_display()}')

    def save(self, *args, **kwargs):
        if not self.dose and self.calculate_dose:
            self.dose = self.dosage_guideline.dosage_per_day(
                weight_in_kgs=self.prescription.weight_in_kgs,
                strength=self.medication.strength,
                strength_units=self.medication.units)
            self.total = float(self.dose) * float(self.rduration.days)
        self.remaining = self.get_remaining()
        self.as_string = str(self)
        super().save(*args, **kwargs)

    @property
    def subject_identifier(self):
        return self.prescription.subject_identifier

    @property
    def rduration(self):
        return (self.end_date - self.start_date)

    @property
    def duration(self):
        display = str(self.rduration)
        return display.split(',')[0]

    def get_remaining(self, exclude_id=None):
        options = {}
        remaining = 0
        if self.total:
            if exclude_id:
                options = dict(id=exclude_id)
            aggregate = self.dispenseditem_set.filter(
                **options).aggregate(Sum('dispensed'))
            total_dispensed = float(aggregate.get(
                'dispensed__sum') or 0.0)
            remaining = float(self.total) - float(total_dispensed)
        return remaining
