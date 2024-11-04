from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import RequestItemForm
from ...models import RequestItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(RequestItem, site=edc_pharmacy_admin)
class RequestItemAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Request item for stock request"
    show_object_tools = False
    show_cancel = True
    form = RequestItemForm
    autocomplete_fields = ["rx"]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "request",
                    "request_item_datetime",
                    "rx",
                )
            },
        ),
        (
            "Section B",
            {
                "classes": ("collapse",),
                "fields": ("code", "gender", "sid", "site"),
            },
        ),
        (
            "Section C",
            {
                "classes": ("collapse",),
                "fields": ("printed_datetime", "printed", "scanned_datetime", "scanned"),
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "request_item_id",
        "item_date",
        "request_changelist",
        "site_number",
        "subject",
        "code",
        "gender",
        "sid",
        "printed",
        "scanned",
        "received",
        "dispensed",
    )
    readonly_fields = (
        "printed_datetime",
        "printed",
        "scanned_datetime",
        "scanned",
        "site",
        "gender",
        "sid",
        "code",
    )

    search_fields = ("code", "id", "rx__subject_identifier", "request__request_identifier")

    @admin.display(description="Date", ordering="request_item_datetime")
    def item_date(self, obj):
        return to_local(obj.request_item_datetime).date()

    @admin.display(description="Subject", ordering="subject_identifier")
    def subject(self, obj):
        return obj.subject_identifier

    @admin.display(description="Site", ordering="site_id")
    def site_number(self, obj):
        return obj.site_id

    @admin.display(description="ITEM#", ordering="request_item_identifier")
    def request_item_id(self, obj):
        return obj.request_item_identifier

    @admin.display(description="Request#")
    def request_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_request_changelist")
        url = f"{url}?q={obj.request.request_identifier}"
        context = dict(
            url=url, label=f"{obj.request.request_identifier}", title="Back to request"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
