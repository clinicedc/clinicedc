import re
from datetime import date, datetime
from typing import Optional, Union

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CharField, DateField, DateTimeField

from .constants import REPORT_DATETIME_FIELD_NAME

ymd_pattern = (
    r"^([0-9]{1,3}y([0-1]?[0-2]m)?([0-9]m)?)$|^([0-1]?"
    r"[0-2]m)$|^([0-9]m)$|^([1-3]?[1-9]d)$|^(0d)$"
)


class InvalidFormat(Exception):
    pass


class InvalidFieldName(Exception):
    pass


def estimated_date_from_ago(
    data: Union[dict, models.Model],
    ago_field: str,
    reference_field: Optional[str] = None,
    future: Optional[bool] = None,
) -> Optional[date]:
    """Wrapper function for `duration_to_date` typically called in
    modelform.clean() and model.save().

    Returns the estimated date using `duration_to_date` or None.

    Will raise an exception if the string cannot be interpreted.
    """

    estimated_date = None
    is_form_data = False
    reference_field = reference_field or REPORT_DATETIME_FIELD_NAME
    raise_on_invalid_field_name(data, ago_field)
    raise_on_invalid_field_name(data, reference_field)
    try:
        ago_str = data.get(ago_field)
        reference_date = data.get(reference_field)
    except AttributeError:
        ago_str = getattr(data, ago_field, None)
        reference_date = getattr(data, reference_field, None)
    else:
        is_form_data = True
    try:
        reference_date = reference_date.date()
    except AttributeError:
        pass
    if ago_str and reference_date:
        try:
            estimated_date = duration_to_date(ago_str, reference_date, future=future)
        except InvalidFormat as e:
            if is_form_data:
                raise forms.ValidationError({ago_field: str(e)})
            raise
    return estimated_date


def duration_to_date(
    duration_text: Union[str, CharField],
    reference_date: Union[date, datetime, DateField, DateTimeField],
    future: Optional[bool] = None,
) -> date:
    """ "Returns the estimated date from a well-formatted string
    relative to a reference date/datetime.

    Will raise an exception if the string cannot be interpreted.
    """
    duration_text = duration_text.replace(" ", "")
    if not re.match(ymd_pattern, duration_text):
        raise InvalidFormat(
            "Expected format `NNyNNm`. e.g: 5y6m, 15y 12m, 12m, 4y... "
            "You may also specify number of days alone, e.g. 7d, 0d... "
            f"Got {duration_text}"
        )
    future = False if future is None else future
    years = 0
    months = 0
    days = 0
    if "y" in duration_text:
        years_str, remaining = duration_text.split("y")
        years = int(years_str)
        if remaining and "m" in remaining:
            months = int(remaining.split("m")[0])
    elif "m" in duration_text:
        months_str = duration_text.split("m")[0]
        months = int(months_str)
    else:
        days_str = duration_text.split("d")[0]
        days = int(days_str)
    delta = relativedelta(years=years, months=months, days=days)
    if future:
        return reference_date + delta
    return reference_date - delta


def raise_on_invalid_field_name(data: Union[dict, models.Model], attrname: str) -> None:
    if attrname is not None:
        try:
            data[attrname]
        except KeyError as e:
            raise InvalidFieldName(f"{e} Got {data}")
        except TypeError:
            try:
                getattr(data, attrname)
            except AttributeError as e:
                raise InvalidFieldName(f"{e} Got {data}")
    else:
        raise InvalidFieldName(f"Field name cannot be None. Got {data}")
    return None


def model_exists_or_raise(
    subject_visit,
    model_cls,
    singleton=None,
) -> bool:
    singleton = False if singleton is None else singleton
    if singleton:
        opts = {"subject_visit__subject_identifier": subject_visit.subject_identifier}
    else:
        opts = {"subject_visit": subject_visit}
    try:
        model_cls.objects.get(**opts)
    except ObjectDoesNotExist:
        raise forms.ValidationError(
            f"Complete the `{model_cls._meta.verbose_name}` CRF first."
        )
    return True
