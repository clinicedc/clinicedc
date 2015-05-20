

def get_upper_window_days(upper_window_value, upper_window_unit):
    """Returns the upper bound in days."""
    if upper_window_unit.upper() == 'D':
        days = upper_window_value * 1
    elif upper_window_unit.upper() == 'M':
        days = upper_window_value * 30
    elif upper_window_unit.upper() == 'Y':
        days = upper_window_value * 365
    elif upper_window_unit.upper() == 'H':
        if upper_window_value <= 24:
            days = 1
        else:
            days = round(upper_window_value / 24, 0)

    else:
        raise TypeError('Invalid upper_window_value, You have the value \'%s\' stored' % (upper_window_unit.upper()))
    return days
