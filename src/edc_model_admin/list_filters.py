from __future__ import annotations

from dateutil.relativedelta import MO, relativedelta
from django.contrib import admin
from django.db.models import QuerySet
from edc_constants.constants import (
    FUTURE_DATE,
    IS_NULL,
    LAST_MONTH,
    LAST_WEEK,
    NEXT_WEEK,
    NOT_NULL,
    PAST_DATE,
    THIS_MONTH,
    THIS_WEEK,
    TODAY,
    TOMORROW,
    YESTERDAY,
)
from edc_utils import get_utcnow


class FutureDateListFilter(admin.SimpleListFilter):
    title = None

    parameter_name = None
    field_name = None

    def lookups(self, request, model_admin) -> tuple:
        return (
            (TODAY, "Today"),
            (TOMORROW, "Tomorrow"),
            (THIS_WEEK, "This week"),
            (NEXT_WEEK, "Next week"),
            (FUTURE_DATE, "Any future date"),
            (PAST_DATE, "Any past date"),
            (IS_NULL, "No date"),
            (NOT_NULL, "Has date"),
        )

    @property
    def extra_queryset_options(self) -> dict:
        return {}

    def queryset(self, request, queryset) -> QuerySet | None:
        morning = get_utcnow().replace(second=0, hour=0, minute=0)
        monday = morning + relativedelta(weekday=MO(-1))
        night = get_utcnow().replace(second=59, hour=23, minute=59)
        qs = None
        if self.value() == NEXT_WEEK:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday + relativedelta(weeks=1),
                    f"{self.field_name}__lt": monday + relativedelta(weeks=2),
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == THIS_WEEK:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday + relativedelta(weeks=1),
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == TODAY:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": morning,
                    f"{self.field_name}__lt": night,
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == TOMORROW:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": night,
                    f"{self.field_name}__lt": night + relativedelta(days=1),
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == LAST_WEEK:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday - relativedelta(weeks=1),
                },
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        if self.value() == PAST_DATE:
            qs = queryset.filter(
                **{f"{self.field_name}__lt": morning},
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        if self.value() == FUTURE_DATE:
            qs = queryset.filter(
                **{f"{self.field_name}__gt": night},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == NOT_NULL:
            qs = queryset.filter(
                **{f"{self.field_name}__isnull": False},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        if self.value() == IS_NULL:
            qs = queryset.filter(
                **{f"{self.field_name}__isnull": True},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        return qs


class PastDateListFilter(admin.SimpleListFilter):
    title = None

    parameter_name = None
    field_name = None

    def lookups(self, request, model_admin) -> tuple:
        return (
            (TODAY, "Today"),
            (YESTERDAY, "Yesterday"),
            (THIS_WEEK, "This week"),
            (LAST_WEEK, "Last week"),
            (THIS_MONTH, "This month"),
            (LAST_MONTH, "Last month"),
            (PAST_DATE, "Any past date"),
            (IS_NULL, "No date"),
            (NOT_NULL, "Has date"),
        )

    @property
    def extra_queryset_options(self) -> dict:
        return {}

    def queryset(self, request, queryset) -> QuerySet | None:
        morning = get_utcnow().replace(second=0, hour=0, minute=0)
        monday = morning + relativedelta(weekday=MO(-1))
        night = get_utcnow().replace(second=59, hour=23, minute=59)
        qs = None
        if self.value() == THIS_WEEK:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday + relativedelta(weeks=1),
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        elif self.value() == TODAY:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": morning,
                    f"{self.field_name}__lt": night,
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        elif self.value() == YESTERDAY:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__lte": night,
                    f"{self.field_name}__lt": night - relativedelta(days=1),
                },
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        elif self.value() == LAST_WEEK:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday - relativedelta(weeks=1),
                },
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        elif self.value() == THIS_MONTH:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday + relativedelta(months=1),
                },
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        elif self.value() == LAST_MONTH:
            qs = queryset.filter(
                **{
                    f"{self.field_name}__gte": monday,
                    f"{self.field_name}__lt": monday - relativedelta(months=1),
                },
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        elif self.value() == PAST_DATE:
            qs = queryset.filter(
                **{f"{self.field_name}__lt": morning},
                **self.extra_queryset_options,
            ).order_by(f"-{self.field_name}")
        elif self.value() == FUTURE_DATE:
            qs = queryset.filter(
                **{f"{self.field_name}__gt": night},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        elif self.value() == NOT_NULL:
            qs = queryset.filter(
                **{f"{self.field_name}__isnull": False},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        elif self.value() == IS_NULL:
            qs = queryset.filter(
                **{f"{self.field_name}__isnull": True},
                **self.extra_queryset_options,
            ).order_by(self.field_name)
        return qs
