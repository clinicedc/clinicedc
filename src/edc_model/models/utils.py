import re

from dateutil.relativedelta import relativedelta


class InvalidFormat(Exception):
    pass


def duration_to_date(duration_text, reference_date, future=None):
    future = False if future is None else future
    if re.match(
        r"^([0-9]{1,3}y([0-1]?[0-2]m)?([0-9]m)?)$|^([0-1]?[0-2]m)$|^([0-9]m)$",
        duration_text,
    ):
        if "y" in duration_text:
            years, remaining = duration_text.split("y")
            years = int(years)
            if remaining and "m" in remaining:
                months = int(remaining.split("m")[0])
            else:
                months = 0
        else:
            years = 0
            months = duration_text.split("m")[0]
            months = int(months)
    else:
        raise InvalidFormat(
            f"Expected NNyNNm, for example 5y6m, 15y12m, 12m, ... Got {duration_text}"
        )
    if future:
        return reference_date + relativedelta(years=years, months=months)
    return reference_date - relativedelta(years=years, months=months)
