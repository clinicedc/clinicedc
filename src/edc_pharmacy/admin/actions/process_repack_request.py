from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext

from ...utils import process_repack_request


@admin.action(description="Process repack request")
def process_repack_request_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        repack_obj = queryset.first()
        if repack_obj.processed:
            messages.add_message(
                request, messages.ERROR, "Nothing to do. Repack request already processed"
            )
        else:
            process_repack_request(repack_obj)
            url = reverse("edc_pharmacy_admin:edc_pharmacy_repackrequest_changelist")
            url = f"{url}?q={repack_obj.id}"
            return HttpResponseRedirect(url)
    return None
