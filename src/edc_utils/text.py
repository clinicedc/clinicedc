import random
import re

import pytz

from arrow.arrow import Arrow

try:
    from django.conf import settings
except ImportError:
    TIME_ZONE = "UTC"
    SHORT_DATETIME_FORMAT = "m/d/Y P"
else:
    TIME_ZONE = settings.TIME_ZONE
    SHORT_DATETIME_FORMAT = settings.SHORT_DATETIME_FORMAT


safe_allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"


def get_safe_random_string(length=12, safe=None, allowed_chars=None):
    safe = True if safe is None else safe
    allowed_chars = allowed_chars or (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL"
        "MNOPQRTUVWXYZ012346789!@#%^&*()?<>.,[]{}"
    )
    if safe:
        allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"
    return "".join([random.choice(allowed_chars) for _ in range(length)])


def convert_php_dateformat(php_format_string):
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
    """Converts from camel case to lowercase divided by underscores.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def formatted_datetime(aware_datetime, php_dateformat=None, tz=None):
    """Returns a formatted datetime string, localized by default.
    """
    php_dateformat = php_dateformat or SHORT_DATETIME_FORMAT
    tz = tz or pytz.timezone(TIME_ZONE)
    utc = Arrow.fromdatetime(aware_datetime)
    local = utc.to(tz)
    return local.datetime.strftime(convert_php_dateformat(php_dateformat))
