from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class HeightField(models.DecimalField):

    description = "Height in cm"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("verbose_name"):
            kwargs["verbose_name"] = "Height:"
        if not kwargs.get("validators"):
            kwargs["validators"] = [MinValueValidator(100.0), MaxValueValidator(230.0)]
        if not kwargs.get("help_text"):
            kwargs["help_text"] = "in centimeters"
        kwargs["max_digits"] = 5
        kwargs["decimal_places"] = 1
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_digits"]
        del kwargs["decimal_places"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
