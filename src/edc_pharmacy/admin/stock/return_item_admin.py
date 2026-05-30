from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import ReturnItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ReturnItem, site=edc_pharmacy_admin)
class ReturnItemAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Return Item"
    change_form_title = "Pharmacy: Return Items"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20
    ordering = ("-return_item_identifier",)

    autocomplete_fields = ("stock",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "return_item_identifier",
                    "return_item_datetime",
                    "return_request",
                    "stock",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "return_request_changelist",
        "return_item_date",
        "stock_changelist",
        "formatted_from_location",
        "formatted_to_location",
    )

    list_filter = (
        "return_request__to_location",
        ("return_item_datetime", DateRangeFilterBuilder()),
        "stock__return_requested",
    )

    search_fields = (
        "id",
        "return_item_identifier",
        "return_request__id",
        "stock__code",
        "stock__allocation__registered_subject__subject_identifier",
    )

    readonly_fields = (
        "return_item_identifier",
        "return_item_datetime",
        "stock",
        "return_request",
    )

    @admin.display(description="RETURN ITEM #", ordering="return_item_identifier")
    def identifier(self, obj):
        return obj.return_item_identifier

    @admin.display(description="Return item date", ordering="return_item_datetime")
    def return_item_date(self, obj):
        return to_local(obj.return_item_datetime).date()

    @admin.display(description="From", ordering="return_request__from_location")
    def formatted_from_location(self, obj):
        return obj.return_request.from_location.display_name

    @admin.display(description="To", ordering="return_request__to_location")
    def formatted_to_location(self, obj):
        return obj.return_request.to_location.display_name

    @admin.display(description="Stock #", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Return #", ordering="return_request__return_identifier")
    def return_request_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_returnrequest_changelist")
        url = f"{url}?q={obj.return_request.id}"
        context = dict(
            url=url,
            label=obj.return_request.return_identifier,
            title="Go to return request",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
