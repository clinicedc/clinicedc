from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WeightField(models.DecimalField):

    description = "Weight in Kg"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("verbose_name"):
            kwargs["verbose_name"] = "Weight:"
        if not kwargs.get("validators"):
            kwargs["validators"] = [MinValueValidator(15), MaxValueValidator(200)]
        if not kwargs.get("help_text"):
            kwargs["help_text"] = "in kg"
        kwargs["max_digits"] = 8
        kwargs["decimal_places"] = 2
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
