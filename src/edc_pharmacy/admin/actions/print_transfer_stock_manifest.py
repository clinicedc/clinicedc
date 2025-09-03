from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.action(description="Print transfer manifest")
def print_transfer_stock_manifest_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:generate_manifest",
            kwargs={"stock_transfer": queryset.first().pk},
        )
        return HttpResponseRedirect(url)
    return None
