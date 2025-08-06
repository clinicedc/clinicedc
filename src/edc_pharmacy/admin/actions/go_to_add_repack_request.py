from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.display(description="Repack stock")
def go_to_add_repack_request_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    elif not getattr(queryset.first(), "confirmation", None):
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Unable to repack. Stock item has not been confirmed."),
        )
    else:
        obj = queryset.first()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_repackrequest_add")
        url = (
            f"{url}?next=edc_pharmacy_admin:edc_pharmacy_repackrequest_changelist,q"
            f"&q={obj.code}&from_stock={obj.id}"
        )
        return HttpResponseRedirect(url)
    return None
