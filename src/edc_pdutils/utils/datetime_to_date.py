import pandas as pd


def datetime_to_date(value):
    """Convert a datetime to date."""
    if pd.notnull(value):
        return value.date()
    else:
        return value
