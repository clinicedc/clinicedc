from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext

from ...models import StorageBin


@admin.display(description="Add stock to storage bin")
def add_to_storage_bin_action(modeladmin, request, queryset: QuerySet[StorageBin]):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:add_to_storage_bin_url",
            kwargs={"storage_bin": queryset.first().id},
        )
        return HttpResponseRedirect(url)
    return None


@admin.display(description="Move stock to selected storage bin")
def move_to_storage_bin_action(modeladmin, request, queryset: QuerySet[StorageBin]):
    url = reverse(
        "edc_pharmacy:move_to_storage_bin_url",
        kwargs={"storage_bin": queryset.first().id},
    )
    return HttpResponseRedirect(url)
