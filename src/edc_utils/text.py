import random
import re
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from django.conf import settings

safe_allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"


def get_safe_random_string(length=12, safe=None, allowed_chars=None):
    safe = True if safe is None else safe
    allowed_chars = allowed_chars or (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL" "MNOPQRTUVWXYZ012346789!@#%^&*()?<>.,[]{}"
    )
    if safe:
        allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"
    return "".join([random.choice(allowed_chars) for _ in range(length)])  # nosec B311


def convert_php_dateformat(php_format_string):
    """Convert a date/datetime using a php format string
    as used by settings.SHORT_DATE_FORMAT.

    For example:
        obj.report_datetime.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )
    """

    php_to_python = {
        "A": "%p",
        "D": "%a",
        "F": "%B",
        "H": "%H",
        "M": "%b",
        "N": "%b",
        "W": "%W",
        "Y": "%Y",
        "d": "%d",
        "e": "%Z",
        "h": "%I",
        "i": "%M",
        "l": "%A",
        "m": "%m",
        "s": "%S",
        "w": "%w",
        "y": "%y",
        "z": "%j",
        "j": "%d",
        "P": "%I:%M %p",
    }
    python_format_string = php_format_string
    for php, py in php_to_python.items():
        python_format_string = python_format_string.replace(php, py)
    return python_format_string


def convert_from_camel(name):
    """Converts from camel case to lowercase divided by underscores."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def formatted_datetime(
    aware_datetime: Optional[datetime],
    php_dateformat: Optional[str] = None,
    tz: Optional[str] = None,
    format_as_date: Optional[bool] = None,
):
    """Returns a formatted datetime string, localized by default.

    format_as_date: does not affect the calculation, just the formatted output.
    """
    formatted = ""
    if aware_datetime:
        local = aware_datetime.astimezone(tz or ZoneInfo(settings.TIME_ZONE))
        if format_as_date:
            php_dateformat = php_dateformat or settings.SHORT_DATE_FORMAT
            formatted = local.date().strftime(convert_php_dateformat(php_dateformat))
        else:
            php_dateformat = php_dateformat or settings.SHORT_DATETIME_FORMAT
            formatted = local.strftime(convert_php_dateformat(php_dateformat))
    return formatted


def formatted_date(dte, php_dateformat=None):
    """Returns a formatted datetime string."""
    if dte:
        php_dateformat = php_dateformat or settings.SHORT_DATE_FORMAT
        return dte.strftime(convert_php_dateformat(php_dateformat))
    return ""
