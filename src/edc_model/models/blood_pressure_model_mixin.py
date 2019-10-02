from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BloodPressureModelMixin(models.Model):

    sys_blood_pressure = models.IntegerField(
        verbose_name="Blood pressure: systolic",
        validators=[MinValueValidator(50), MaxValueValidator(220)],
        null=True,
        blank=False,
        help_text="in mm. format SYS, e.g. 120",
    )

    dia_blood_pressure = models.IntegerField(
        verbose_name="Blood pressure: diastolic",
        validators=[MinValueValidator(20), MaxValueValidator(150)],
        null=True,
        blank=False,
        help_text="in Hg. format DIA, e.g. 80",
    )

    class Meta:
        abstract = True
