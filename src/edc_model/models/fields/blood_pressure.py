from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SystolicPressureField(models.IntegerField):

    description = "Systolic pressure"

    def __init__(self, *args, verbose_name=None, **kwargs):
        kwargs["verbose_name"] = verbose_name or "Blood pressure: systolic"
        kwargs["validators"] = [MinValueValidator(50), MaxValueValidator(300)]
        kwargs["help_text"] = "in mm. format SYS, e.g. 120"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs


class DiastolicPressureField(models.IntegerField):

    description = "Diastolic pressure"

    def __init__(self, *args, verbose_name=None, **kwargs):
        kwargs["verbose_name"] = verbose_name or "Blood pressure: diastolic"
        kwargs["validators"] = [MinValueValidator(20), MaxValueValidator(225)]
        kwargs["help_text"] = "in Hg. format DIA, e.g. 80"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
