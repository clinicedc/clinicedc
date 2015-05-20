

def get_lower_window_days(lower_window_value, lower_window_unit):
    """Returns the lower bound in days."""
    if lower_window_unit.upper() == 'D':
        days = lower_window_value * 1
    elif lower_window_unit.upper() == 'M':
        days = lower_window_value * 30
    elif lower_window_unit.upper() == 'Y':
        days = lower_window_value * 365
    elif lower_window_unit.upper() == 'H':
        if lower_window_value <= 24:
            days = 1
        else:
            days = round(lower_window_value / 24, 0)
    else:
        raise TypeError('Invalid lower_window_value, You have the value \'%s\' stored' % (lower_window_unit.upper()))
    return days
