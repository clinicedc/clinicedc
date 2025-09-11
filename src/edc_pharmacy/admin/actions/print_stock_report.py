from __future__ import annotations

from uuid import uuid4

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _


@admin.action(description=_("Print stock report"))
def print_stock_report_action(modeladmin, request, queryset):
    if queryset.count() > 1:
        session_uuid = str(uuid4())
        request.session[session_uuid] = list(queryset.values_list("pk", flat=True))
        url = reverse("edc_pharmacy:stock_report", kwargs={"session_uuid": session_uuid})
        return HttpResponseRedirect(url)
    return None
