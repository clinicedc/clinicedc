from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WaistCircumferenceField(models.DecimalField):

    description = "Waist circumference"

    def __init__(self, *args, **kwargs):
        kwargs["verbose_name"] = "Waist circumference:"
        kwargs["max_digits"] = 5
        kwargs["decimal_places"] = 1
        kwargs["validators"] = [MinValueValidator(50.0), MaxValueValidator(175.0)]
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
