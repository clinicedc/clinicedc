from warnings import warn

from django.db import models

from ..validators import ymd_validator


class DurationYMDField(models.CharField):

    description = "Duration in y/m"

    def __init__(self, *args, **kwargs) -> None:
        kwargs["verbose_name"] = kwargs.get("verbose_name") or "Duration:"
        kwargs["max_length"] = 8
        kwargs["validators"] = [ymd_validator]
        kwargs["help_text"] = (
            f"{kwargs.get('help_text') or ''} Format is `YYyMMm` or `DDd`. "
            "For example 3y10m, 12y7m ... or 7d, 0d ..."
        )
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["verbose_name"]
        del kwargs["max_length"]
        del kwargs["validators"]
        del kwargs["help_text"]
        return name, path, args, kwargs


class DurationYearMonthField(DurationYMDField):
    def __init__(self, *args, **kwargs) -> None:
        warn(
            "DurationYearMonthField has been deprecated. Use DurationYMDField instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
