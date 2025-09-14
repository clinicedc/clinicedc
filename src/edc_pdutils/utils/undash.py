import re

import pandas as pd


def undash(value, exclude_pattern=None):
    if pd.notnull(value):
        try:
            if exclude_pattern:
                if not re.match(exclude_pattern, value):
                    value = value.replace("-", "")
            else:
                value = value.replace("-", "")
        except AttributeError as e:
            raise AttributeError(f"{e!s}. Got '{value}'")
    return value
