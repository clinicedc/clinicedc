"""Telling a notebook that the frame it is holding is behind.

The frames themselves are queries, not tables: calling one again always
reflects the database as it stands. What goes stale is a dataframe held
in a notebook, or a spreadsheet someone exported on Tuesday and is still
working through on Friday. `result_expected` in particular is a
user-driven change, so a worklist pulled before a site edited its
requisitions will overstate the work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from clinicedc_constants import NO
from django.apps import apps as django_apps
from django.conf import settings
from django.utils import timezone

from ..models import Result

if TYPE_CHECKING:
    from datetime import datetime

__all__ = [
    "PULLED_DATETIME",
    "changed_since_pulled",
    "get_pulled_datetime",
    "results_changed_since",
    "stamp_pulled_datetime",
]

PULLED_DATETIME = "pulled_datetime"


def stamp_pulled_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` carrying the moment it was read.

    `DataFrame.attrs` survives being held in a notebook but not a round
    trip through CSV, so an exported worklist loses this. Note the
    timestamp alongside the export if it matters.
    """
    df.attrs[PULLED_DATETIME] = timezone.now()
    return df


def get_pulled_datetime(df: pd.DataFrame) -> datetime | None:
    """Return when `df` was read, or None if it does not say."""
    return df.attrs.get(PULLED_DATETIME)


def results_changed_since(since: datetime) -> dict[str, int]:
    """Return counts of what has changed since `since`.

    Any non-zero count means a frame read at `since` is behind and
    should be read again.

    `requisitions_not_expecting_a_result` is the count a worklist cares
    about most: a site deciding no result will ever arrive is what turns
    a missing result from a problem into an explained absence.

    Only counts are returned. For what actually changed, and who changed
    it, read the historical model, for example
    `Requisition.history.filter(history_date__gte=since)`.
    """
    requisition_model_cls = django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)
    requisitions = requisition_model_cls.objects.filter(modified__gte=since)
    return {
        "requisitions_modified": requisitions.count(),
        "requisitions_not_expecting_a_result": requisitions.filter(result_expected=NO).count(),
        "results_imported": Result.objects.filter(created__gte=since).count(),
        "results_modified": Result.objects.filter(modified__gte=since).count(),
    }


def changed_since_pulled(df: pd.DataFrame) -> dict[str, int]:
    """Return counts of what has changed since `df` was read.

    Returns an empty dict where the frame does not carry a pull
    timestamp, which is not the same as nothing having changed.
    """
    since = get_pulled_datetime(df)
    if since is None:
        return {}
    return results_changed_since(since)
