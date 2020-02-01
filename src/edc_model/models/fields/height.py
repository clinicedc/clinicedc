from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class HeightField(models.DecimalField):

    description = "Height in cm"

    def __init__(self, *args, **kwargs):
        kwargs["verbose_name"] = "Height:"
        kwargs["max_digits"] = 5
        kwargs["decimal_places"] = 1
        kwargs["validators"] = [MinValueValidator(100.0), MaxValueValidator(230.0)]
        kwargs["help_text"] = "in centimeters"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
