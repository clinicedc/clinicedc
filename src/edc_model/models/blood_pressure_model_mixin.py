from django.db import models
from .fields import SystolicPressureField, DiastolicPressureField


class BloodPressureModelMixin(models.Model):

    sys_blood_pressure = SystolicPressureField(null=True, blank=False,)

    dia_blood_pressure = DiastolicPressureField(null=True, blank=False,)

    class Meta:
        abstract = True
