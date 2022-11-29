from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Optional, Union

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CharField, DateField, DateTimeField, Model

from .constants import REPORT_DATETIME_FIELD_NAME

dh_pattern = r"^(([0-9]{1,3}d)?((2[0-3]|[01]?[0-9])h)?)$"

ymd_pattern = (
    r"^([0-9]{1,3}y([0-1]?[0-2]m)?([0-9]m)?)$|^([0-1]?"
    r"[0-2]m)$|^([0-9]m)$|^([1-3]?[1-9]d)$|^(0d)$"
)


class InvalidFormat(Exception):
    pass


class InvalidFieldName(Exception):
    pass


def estimated_date_from_ago(
    cleaned_data: dict = None,
    instance: Model = None,
    ago_field: str = None,
    reference_field: str = None,
    future: bool | None = None,
) -> Optional[date]:
    """Wrapper function for `duration_to_date` typically called in
    modelform.clean() and model.save().

    Returns the estimated date using `duration_to_date` or None.

    Will raise an exception if the string cannot be interpreted.
    """

    estimated_date = None
    data = instance or cleaned_data
    reference_field = reference_field or REPORT_DATETIME_FIELD_NAME
    raise_on_invalid_field_name(data, ago_field)
    raise_on_invalid_field_name(data, reference_field)
    try:
        ago_str = data.get(ago_field)
        reference_date = data.get(reference_field)
    except AttributeError:
        ago_str = getattr(data, ago_field, None)
        reference_date = getattr(data, reference_field, None)
    try:
        reference_date = reference_date.date()
    except AttributeError:
        pass
    if ago_str and reference_date:
        try:
            estimated_date = duration_to_date(ago_str, reference_date, future=future)
        except InvalidFormat as e:
            if cleaned_data:
                raise forms.ValidationError({ago_field: str(e)})
            raise
    return estimated_date


def duration_to_date(
    duration_text: Union[str, CharField],
    reference_date: Union[date, datetime, DateField, DateTimeField],
    future: Optional[bool] = None,
) -> date:
    """Returns the estimated date from a well-formatted string
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
        raise ObjectDoesNotExist(f"{model_cls._meta.verbose_name} does not exist.")
    return True


def is_inline_model(instance):
    """See also, edc-crf inline model mixin."""
    try:
        instance._meta.crf_inline_parent
    except AttributeError:
        return False
    return True


def timedelta_from_duration_dh_field(
    data: Union[dict, models.Model], duration_dh_field: str
) -> Optional[timedelta]:
    """Wrapper function for `duration_dh_to_timedelta` typically called in
    modelform.clean() and model.save().

    Returns timedelta using `duration_dh_to_timedelta` or None.

    Will raise an exception if the string cannot be interpreted.
    """
    duration_timedelta = None
    is_form_data = False
    raise_on_invalid_field_name(data, duration_dh_field)
    try:
        duration_dh_str = data.get(duration_dh_field)
    except AttributeError:
        duration_dh_str = getattr(data, duration_dh_field, None)
    else:
        is_form_data = True

    if duration_dh_str:
        try:
            duration_timedelta = duration_dh_to_timedelta(duration_text=duration_dh_str)
        except InvalidFormat as e:
            if is_form_data:
                raise forms.ValidationError({duration_dh_field: str(e)})
            raise
    return duration_timedelta


def duration_dh_to_timedelta(duration_text: Union[str, CharField]) -> timedelta:
    """Returns timedelta from a well-formatted string
    (specified in days and/or hours).

    Will raise an exception if the string cannot be interpreted.
    """
    duration_text = duration_text.replace(" ", "")
    if not re.match(dh_pattern, duration_text):
        raise InvalidFormat(
            "Expected format is `DDdHHh`, `DDd` or `HHh`. "
            "For example 1d23h, 15d9h ... or 20d, or 5h ..."
            f"Got {duration_text}"
        )
    days = 0
    hours = 0
    if "d" in duration_text:
        days_str, remaining = duration_text.split("d")
        days = int(days_str)
        if remaining and "h" in remaining:
            hours = int(remaining.split("h")[0])
    else:
        hours_str = duration_text.split("h")[0]
        hours = int(hours_str)
    return timedelta(days=days, hours=hours)
