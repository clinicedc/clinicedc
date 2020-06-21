from django.db import models

from ..validators import ym_validator


class DurationYearMonthField(models.CharField):

    description = "Duration in y/m"

    def __init__(self, *args, **kwargs):
        kwargs["verbose_name"] = "Duration:"
        kwargs["max_length"] = 8
        kwargs["validators"] = [ym_validator]
        kwargs["help_text"] = "Format is `YYyMMm`. For example 1y11m, 12y7m, etc"
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_length"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs
