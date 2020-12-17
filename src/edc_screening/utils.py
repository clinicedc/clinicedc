from django.conf import settings
from django.utils.html import format_html
from edc_constants.constants import NORMAL, YES, NO


def if_yes(value):
    """Returns True if value is YES."""
    if value == NORMAL:
        return True
    return value == YES


def if_no(value):
    """Returns True if value is NO."""
    return value == NO


def if_normal(value):
    """Returns True if value is NORMAL."""
    return value == NORMAL


def get_subject_screening_model():
    return getattr(settings, "SUBJECT_SCREENING_MODEL", None)


def format_reasons_ineligible(*str_values, delimiter=None):
    reasons = None
    delimiter = delimiter or "|"
    str_values = [x for x in str_values if x is not None]
    if str_values:
        str_values = "".join(str_values)
        reasons = format_html(str_values.replace(delimiter, "<BR>"))
    return reasons


def eligibility_display_label(eligible):
    return "ELIGIBLE" if eligible else "not eligible"
