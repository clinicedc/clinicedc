import re

from dateutil.relativedelta import relativedelta

ymd_pattern = (
    r"^([0-9]{1,3}y([0-1]?[0-2]m)?([0-9]m)?)$|^([0-1]?"
    r"[0-2]m)$|^([0-9]m)$|^([1-3]?[1-9]d)$|^(0d)$"
)


class InvalidFormat(Exception):
    pass


def duration_to_date(duration_text, reference_date, future=None):
    future = False if future is None else future
    if re.match(ymd_pattern, duration_text):
        if "y" in duration_text:
            years, remaining = duration_text.split("y")
            years = int(years)
            if remaining and "m" in remaining:
                months = int(remaining.split("m")[0])
            else:
                months = 0
            days = 0
        elif "m" in duration_text:
            years = 0
            months = duration_text.split("m")[0]
            months = int(months)
            days = 0
        else:
            years = 0
            months = 0
            days = duration_text.split("d")[0]
            days = int(days)
    else:
        raise InvalidFormat(
            "Expected format `NNyNNm`. e.g: 5y6m, 15y12m, 12m, 4y... "
            "You may also specify number of days alone, e.g. 7d, 0d... "
            f"No spaces allowed. Got {duration_text}"
        )
    delta = relativedelta(years=years, months=months, days=days)
    if future:
        return reference_date + delta
    return reference_date - delta
