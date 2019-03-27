from math import ceil
from uuid import uuid4

from .age import age, get_dob, formatted_age, get_age_in_days, AgeValueError  # noqa
from .date import get_utcnow, to_arrow_utc, to_utc  # noqa
from .show_urls import show_urls, show_url_names  # noqa
from .text import (  # noqa
    safe_allowed_chars,  # noqa
    get_safe_random_string,  # noqa
    convert_php_dateformat,  # noqa
    convert_from_camel,  # noqa
    formatted_datetime,  # noqa
)  # noqa


def get_uuid():
    return uuid4().hex


def round_up(value, digits):
    ceil(value * (10 ** digits)) / (10 ** digits)
