from django.db import models
from edc_utils import get_utcnow

from edc_vitals.model_mixins import (
    BloodPressureModelMixin,
    SimpleBloodPressureModelMixin,
    WeightHeightBmiModelMixin,
)


class BloodPressure(BloodPressureModelMixin, models.Model):
    pass


class SimpleBloodPressure(SimpleBloodPressureModelMixin, models.Model):
    pass


class WeightHeightBmi(WeightHeightBmiModelMixin, models.Model):

    report_datetime = models.DateTimeField(default=get_utcnow)

    dob = models.DateField(null=True)
