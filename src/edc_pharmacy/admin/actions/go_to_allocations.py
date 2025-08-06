from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.display(description="Go to allocations")
def go_to_allocations(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={queryset.first().id}"
        return HttpResponseRedirect(url)
    return None
