from django.db import models

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
    pass
