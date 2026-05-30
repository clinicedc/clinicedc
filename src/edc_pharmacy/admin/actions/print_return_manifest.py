from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.action(description="Print return manifest")
def print_return_manifest_action(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:return_manifest_url",
            kwargs={"return_request": queryset.first().pk},
        )
        return HttpResponseRedirect(url)
    return None
