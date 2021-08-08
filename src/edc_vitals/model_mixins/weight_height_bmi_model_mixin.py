from django.db import models
from edc_reportable import calculate_bmi

from ..models import HeightField, WeightField


class WeightHeightBmiModelMixin(models.Model):

    lower_bmi_value = 15.0

    upper_bmi_value = 60.0

    weight = WeightField(null=True, blank=True)

    height = HeightField(null=True, blank=True)

    calculated_bmi_value = models.DecimalField(
        verbose_name="BMI",
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=False,
        help_text="system calculated",
    )

    def save(self, *args, **kwargs):
        bmi = self.calculate_bmi()
        self.calculated_bmi_value = bmi.value if bmi else None
        super().save(*args, **kwargs)

    def calculate_bmi(self):
        return calculate_bmi(
            weight_kg=self.weight,
            height_cm=self.height,
            lower_bmi_value=self.lower_bmi_value,
            upper_bmi_value=self.upper_bmi_value,
            report_datetime=self.report_datetime,
            dob=self.get_dob(),
        )

    def get_dob(self):
        """Override to provides DoB if not on the model"""
        return None

    class Meta:
        abstract = True
