from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext

if TYPE_CHECKING:
    from ...models import Receive, RepackRequest


@admin.display(description="Confirm repacked and labeled stock")
def confirm_repacked_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest]):
    return confirm_stock_action(modeladmin, request, queryset)


@admin.display(description="Confirm labeled stock")
def confirm_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest | Receive]):
    """See also : utils.confirm_stock"""
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:confirm_stock_url",
            kwargs={
                "source_pk": str(queryset.first().id),
                "model": queryset.model._meta.label_lower.split(".")[1],
            },
        )
        return HttpResponseRedirect(url)
    return None
