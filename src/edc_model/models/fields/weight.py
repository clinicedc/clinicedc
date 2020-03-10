from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class WeightField(models.DecimalField):

    description = "Weight in Kg"

    def __init__(self, *args, **kwargs):
        kwargs["verbose_name"] = "Weight:"
        kwargs["max_digits"] = 8
        kwargs["decimal_places"] = 2
        kwargs["validators"] = [MinValueValidator(15), MaxValueValidator(200)]
        kwargs["help_text"] = "in kg"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
