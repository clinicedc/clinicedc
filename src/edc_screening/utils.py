from edc_constants.constants import NORMAL, YES, NO


def if_yes(value):
    if value == NORMAL:
        return True
    return value == YES


def if_no(value):
    return value == NO


def if_normal(value):
    return value == NORMAL
