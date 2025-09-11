from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class HeartRateField(models.IntegerField):
    description = "Heart rate in BPM"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("verbose_name"):
            kwargs["verbose_name"] = "Heart rate:"
        if not kwargs.get("validators"):
            kwargs["validators"] = [MinValueValidator(30), MaxValueValidator(200)]
        if not kwargs.get("help_text"):
            kwargs["help_text"] = "BPM"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
