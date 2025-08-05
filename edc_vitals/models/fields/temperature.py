from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TemperatureField(models.DecimalField):
    description = "Temperature in degrees Celsius"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("verbose_name"):
            kwargs["verbose_name"] = "Temperature:"
        if not kwargs.get("validators"):
            kwargs["validators"] = [MinValueValidator(30), MaxValueValidator(45)]
        if not kwargs.get("help_text"):
            kwargs["help_text"] = "in degrees Celsius"
        kwargs["max_digits"] = 3
        kwargs["decimal_places"] = 1
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["validators"]
        del kwargs["help_text"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        return name, path, args, kwargs
