import re
from datetime import date, datetime

from ...exceptions import ValueBoundryError
from .get_normal_data_or_raise import get_normal_data_or_raise


def in_bounds_or_raise(
    name: str,
    value: int | float,
    units: str = None,
    gender: str = None,
    dob: date = None,
    report_datetime: datetime = None,
    age_units: str | None = None,
) -> bool:
    """Raises a ValueBoundryError exception if condition not met.

    Condition is evaluated to True or False as a string
    constructed from given parameters.

    For example,
        "lower lower_operator value upper_operator upper"
        "1.7<3.6<=3.5"
        "7.3<3.6"
    """

    pattern = r"([<>]=?|==|!=)?\s*-?\d+(\.\d+)?"

    value = float(value)
    obj = get_normal_data_or_raise(
        label=name,
        units=units,
        gender=gender,
        dob=dob,
        report_datetime=report_datetime,
        age_units=age_units,
    )
    condition_str = (
        f'{"" if obj.lower is None else obj.lower}{obj.lower_operator or ""}{value}'
        f'{obj.upper_operator or ""}{"" if obj.upper is None else obj.upper}'
    )
    if not re.match(pattern, condition_str):
        raise ValueError(f"Invalid condition string. Got {condition_str}.")
    print(condition_str)
    if not eval(condition_str):  # nosec B307
        raise ValueBoundryError(f"{name}: {condition_str}{units} [{gender}]")
    return True
