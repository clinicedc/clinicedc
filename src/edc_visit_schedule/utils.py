from edc_visit_schedule.constants import DAY, MONTH, YEAR, HOUR


def get_lower_window_days(lower_window_value, lower_window_unit):
    """Returns the lower bound in days."""
    if lower_window_unit.upper() == DAY:
        days = lower_window_value * 1
    elif lower_window_unit.upper() == MONTH:
        days = lower_window_value * 30
    elif lower_window_unit.upper() == YEAR:
        days = lower_window_value * 365
    elif lower_window_unit.upper() == HOUR:
        if lower_window_value <= 24:
            days = 1
        else:
            days = round(lower_window_value / 24, 0)
    else:
        raise TypeError('Invalid lower_window_value, You have the value \'%s\' stored' % (lower_window_unit.upper()))
    return days


def get_upper_window_days(upper_window_value, upper_window_unit):
    """Returns the upper bound in days."""
    if upper_window_unit.upper() == DAY:
        days = upper_window_value * 1
    elif upper_window_unit.upper() == MONTH:
        days = upper_window_value * 30
    elif upper_window_unit.upper() == YEAR:
        days = upper_window_value * 365
    elif upper_window_unit.upper() == HOUR:
        if upper_window_value <= 24:
            days = 1
        else:
            days = round(upper_window_value / 24, 0)

    else:
        raise TypeError('Invalid upper_window_value, You have the value \'%s\' stored' % (upper_window_unit.upper()))
    return days
