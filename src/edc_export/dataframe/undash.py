import pandas as pd
import re


def undash(value, exclude_pattern=None):
    if pd.notnull(value):
        try:
            if exclude_pattern:
                if not re.match(exclude_pattern, value):
                    value = value.replace('-', '')
            else:
                value = value.replace('-', '')
        except AttributeError as e:
            raise AttributeError('{}. Got \'{}\''.format(str(e), value))
    return value
