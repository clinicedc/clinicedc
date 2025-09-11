from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RespiratoryRateField(models.IntegerField):
    description = "Respiratory rate in breaths/min"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("verbose_name"):
            kwargs["verbose_name"] = "Respiratory rate:"
        if not kwargs.get("validators"):
            kwargs["validators"] = [MinValueValidator(6), MaxValueValidator(50)]
        if not kwargs.get("help_text"):
            kwargs["help_text"] = "breaths/min"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
