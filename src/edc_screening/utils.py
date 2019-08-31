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
