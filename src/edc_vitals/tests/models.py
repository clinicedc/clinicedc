from django.db import models
from edc_utils import get_utcnow

from edc_vitals.model_mixins import (
    BloodPressureModelMixin,
    SimpleBloodPressureModelMixin,
    WeightHeightBmiModelMixin,
)
from edc_vitals.models import HeartRateField, RespiratoryRateField, TemperatureField


class BloodPressure(BloodPressureModelMixin, models.Model):
    pass


class HeartRate(models.Model):
    heart_rate = HeartRateField(
        null=True,
        blank=True,
    )


class RespiratoryRate(models.Model):
    respiratory_rate = RespiratoryRateField(
        null=True,
        blank=True,
    )


class SimpleBloodPressure(SimpleBloodPressureModelMixin, models.Model):
    pass


class Temperature(models.Model):
    temperature = TemperatureField(
        null=True,
        blank=True,
    )


class WeightHeightBmi(WeightHeightBmiModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=get_utcnow)

    dob = models.DateField(null=True)
