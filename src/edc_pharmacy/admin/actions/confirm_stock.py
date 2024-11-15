from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext

if TYPE_CHECKING:
    from ...models import Receive, RepackRequest


@admin.display(description="Confirm repacked and labeled stock")
def confirm_repacked_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest]):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        return confirm_stock_from_instance(modeladmin, request, queryset)
    return None


@admin.display(description="Confirm received and labeled stock")
def confirm_received_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest]):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        return confirm_stock_from_instance(modeladmin, request, queryset)
    return None


@admin.display(description="Confirm labeled stock")
def confirm_stock_from_instance(
    modeladmin, request, queryset: QuerySet[RepackRequest | Receive]
):
    """See also : utils.confirm_stock"""
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:confirm_stock_from_instance_url",
            kwargs={
                "source_pk": str(queryset.first().id),
                "model": queryset.model._meta.label_lower.split(".")[1],
            },
        )
        return HttpResponseRedirect(url)
    return None


@admin.display(description="Confirm labeled stock")
def confirm_stock_from_queryset(
    modeladmin, request, queryset: QuerySet[RepackRequest | Receive]
):
    if queryset.count() > 0:
        session_uuid = str(uuid4())
        stock_pks = queryset.values_list("pk", flat=True)
        request.session[session_uuid] = [str(o) for o in stock_pks]
        url = reverse(
            "edc_pharmacy:confirm_stock_from_queryset_url",
            kwargs={"session_uuid": session_uuid},
        )
        return HttpResponseRedirect(url)
    return None
