from __future__ import annotations

from collections.abc import Callable


class FC:
    """A simple class of the eligible criteria for a field.

    value: value expected IF ELIGIBLE
    msg: message if value is NOT met / ineligible
    ignore_if_missing: skip assessment if the field does not have a value

    if value is a callable it must return True/False, True means eligible.
    """

    def __init__(
        self,
        value: str | list | tuple | range | Callable[..., bool] | None = None,
        msg: str | None = None,
        ignore_if_missing: bool | None = False,
        missing_value: str | None = None,
    ):
        self.value = value
        self.msg = msg
        self.ignore_if_missing = ignore_if_missing
        self.missing_value = missing_value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value, self.msg, self.ignore_if_missing})"
