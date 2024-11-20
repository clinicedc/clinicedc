from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext


@admin.display(description="Allocate stock to subject")
def allocate_stock_to_subject(modeladmin, request, queryset):
    """
    1. is there an open unprocess stock request?
    2. what stock is available at the site?
    3. what stock is available at central?

    """
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        url = reverse(
            "edc_pharmacy:allocate_url",
            args=(queryset.first().id,),
        )
        return HttpResponseRedirect(url)
    return None
