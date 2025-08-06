from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.action(description="Scan items to transfer to site")
def transfer_stock_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:transfer_stock_url", kwargs={"stock_transfer": queryset.first().pk}
        )
        return HttpResponseRedirect(url)
    return None
