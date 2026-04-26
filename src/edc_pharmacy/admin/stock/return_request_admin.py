from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import ReturnRequest, ReturnItem
from ..actions import print_return_manifest_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ReturnRequest, site=edc_pharmacy_admin)
class ReturnRequestAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Return Request"
    change_form_title = "Pharmacy: Return Requests"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20
    ordering = ("-return_identifier",)

    autocomplete_fields = ("from_location", "to_location")
    actions = (print_return_manifest_action,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "return_identifier",
                    "return_datetime",
                    "from_location",
                    "to_location",
                    "item_count",
                )
            },
        ),
        (
            "Comment",
            {
                "fields": ("comment",)
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "return_date",
        "formatted_location",
        "n_expected",
        "return_item_changelist",
        "stock_changelist",
        "manifest_link",
    )

    list_filter = (
        ("return_datetime", DateRangeFilterBuilder()),
        "from_location",
        "to_location",
    )

    search_fields = (
        "id",
        "return_identifier",
        "returnitem__stock__code",
        "returnitem__stock__current_allocation__registered_subject__subject_identifier",
    )

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        fields = super().get_readonly_fields(request, obj)
        if obj:
            fields = (
                *fields,
                "return_identifier",
                "return_datetime",
                "from_location",
                "to_location",
                "item_count",
            )
        return fields

    @admin.display(description="RETURN #", ordering="return_identifier")
    def identifier(self, obj):
        return obj.return_identifier

    @admin.display(description="Return date", ordering="return_datetime")
    def return_date(self, obj):
        return to_local(obj.return_datetime).date()

    @admin.display(description="Location")
    def formatted_location(self, obj):
        return f"{obj.from_location} >> {obj.to_location}"

    @admin.display(description="Expected", ordering="item_count")
    def n_expected(self, obj):
        actual = ReturnItem.objects.filter(return_request=obj).count()
        if actual != obj.item_count:
            return f"{actual}/{obj.item_count}"
        return obj.item_count

    @admin.display(description="Items")
    def return_item_changelist(self, obj):
        count = ReturnItem.objects.filter(return_request=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_returnitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=count, title="Go to return items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Manifest")
    def manifest_link(self, obj):
        if not ReturnItem.objects.filter(return_request=obj).exists():
            return "-"
        url = reverse("edc_pharmacy:return_manifest_url", kwargs={"return_request": obj.pk})
        context = dict(url=url, label="PDF", title="Print return manifest")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
