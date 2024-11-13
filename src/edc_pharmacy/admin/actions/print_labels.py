from uuid import uuid4

from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse


@admin.action(description="Print labels")
def print_labels(modeladmin, request, queryset):
    selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
    session_uuid = str(uuid4())
    request.session[session_uuid] = selected
    url = reverse(
        "edc_pharmacy:print_labels_url",
        kwargs={"session_uuid": session_uuid, "model": "stock"},
    )
    return HttpResponseRedirect(url)
