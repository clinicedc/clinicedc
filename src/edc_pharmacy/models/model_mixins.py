from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import YES_NO
from edc_constants.constants import YES

from ..exceptions import NextPrescriptionRefillError
from .dosage_guideline import DosageGuideline
from .formulation import Formulation
from .medication_stock import MedicationStock


class StudyMedicationModelMixin(models.Model):

    """Declare with field subject_visit using a CRF model mixin"""

    dosage_guideline = models.ForeignKey(
        DosageGuideline, on_delete=PROTECT, null=True, blank=False
    )

    formulation = models.ForeignKey(
        Formulation, on_delete=PROTECT, null=True, blank=False
    )

    number_of_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate relative to the next scheduled appointment",
    )

    special_instructions = models.TextField(null=True, blank=True)

    order_next = models.CharField(
        verbose_name="Order medication for next visit?",
        max_length=15,
        choices=YES_NO,
        default=YES,
    )

    next_dosage_guideline = models.ForeignKey(
        DosageGuideline,
        on_delete=PROTECT,
        related_name="next_dosageguideline",
        null=True,
        blank=True,
    )

    next_formulation = models.ForeignKey(
        Formulation,
        on_delete=PROTECT,
        related_name="next_formulation",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Study Medication"
        verbose_name_plural = "Study Medication"
        abstract = True


class StudyMedicationCrfModelMixin(StudyMedicationModelMixin):

    """Declare with a `subject_visit` field attr"""

    @property
    def creates_refills_from_crf(self) -> bool:
        """Attribute for signal"""
        return True

    def save(self, *args, **kwargs):
        if not self.number_of_days:
            self.number_of_days = self.calculate_number_of_days()
        if self.order_next == YES and not self.has_next_appointment:
            raise NextPrescriptionRefillError(
                "Cannot order next refill. This subject has no future appointments."
            )
        super().save(*args, **kwargs)

    @property
    def has_next_appointment(self):
        return self.subject_visit.appointment.next

    def get_subject_identifier(self):
        return self.subject_visit.subject_identifier

    def calculate_number_of_days(self) -> int:
        if self.subject_visit.appointment.next:
            tdelta = (
                self.subject_visit.appointment.next.appt_datetime.date()
                - self.subject_visit.report_datetime.date()
            )
            return tdelta.days
        return 0

    class Meta(StudyMedicationModelMixin.Meta):
        abstract = True


class MedicationOrderModelMixin(models.Model):

    medication_stock = models.ForeignKey(
        MedicationStock,
        null=True,
        blank=False,
        on_delete=PROTECT,
    )

    qty = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)

    packed = models.BooleanField(default=False)
    packed_datetime = models.DateTimeField(null=True, blank=True)

    shipped = models.BooleanField(default=False)
    shipped_datetime = models.DateTimeField(null=True, blank=True)

    received_at_site = models.BooleanField(default=False)
    received_at_site_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
