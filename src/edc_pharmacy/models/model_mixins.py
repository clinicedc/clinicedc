# from django.core.validators import MinValueValidator
# from django.db import models
# from django.db.models.deletion import PROTECT
#
# from ..choices import TIMING
# from .dosage_guideline import DosageGuideline
# from .medication import Medication
#
#
# class PrescriptionItemModelMixin(models.Model):
#
#     name = models.CharField(max_length=150, unique=True)
#
#     medication = models.ForeignKey(Medication, on_delete=PROTECT)
#
#     dosage_guideline = models.ForeignKey(DosageGuideline, on_delete=PROTECT)
#
#     dose = models.DecimalField(
#         max_digits=6,
#         decimal_places=1,
#         null=True,
#         blank=True,
#         help_text="Leave blank to auto-calculate",
#     )
#
#     calculate_dose = models.BooleanField(default=True)
#
#     frequency = models.IntegerField(validators=[MinValueValidator(1)])
#
#     frequency_units = models.CharField(
#         verbose_name="per", max_length=10, default="day", choices=TIMING
#     )
#
#     notes = models.TextField(
#         max_length=250,
#         null=True,
#         blank=True,
#         help_text="Additional information for patient",
#     )
#
#     verified = models.BooleanField(default=False)
#
#     verified_datetime = models.DateTimeField(null=True, blank=True)
#
#     as_string = models.CharField(max_length=150, editable=False)
#
#     def __str__(self):
#         return (
#             f"{str(self.medication)} * {self.dose} "
#             f"{self.medication.get_formulation_display()}(s) "
#             f"{self.frequency} {self.get_frequency_units_display()}"
#         )
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#
#     class Meta:
#         abstract = True
