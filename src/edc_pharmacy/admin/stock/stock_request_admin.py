from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestForm
from ...models import StockRequest, StockRequestItem
from ..actions import create_request_items_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockRequest, site=edc_pharmacy_admin)
class StockRequestAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Request for stock"
    show_object_tools = True
    show_cancel = True
    autocomplete_fields = ["container", "formulation", "site_proxy"]
    form = StockRequestForm

    actions = [create_request_items_action]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "request_identifier",
                    "request_datetime",
                    "site_proxy",
                )
            },
        ),
        (
            "Section B",
            {"fields": ("formulation", "container", "containers_per_subject")},
        ),
        (
            "Section C",
            {"fields": ("item_count", "status")},
        ),
        (
            "Section D",
            {"fields": ("labels",)},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "stock_request_id",
        "request_date",
        "site_proxy",
        "formulation",
        "container",
        "per_subject",
        "request_item_count",
        "add_stock_request_item",
        "stock_request_items",
        "status",
    )

    list_filter = (
        "request_datetime",
        "status",
        "formulation",
        "container",
    )

    radio_fields = {
        "status": admin.VERTICAL,
    }

    search_fields = ["id", "request_identifier"]

    @admin.display(description="Request #", ordering="request_identifier")
    def stock_request_id(self, obj):
        return obj.request_identifier

    @admin.display(description="Per", ordering="containers_per_subject")
    def per_subject(self, obj):
        return obj.containers_per_subject

    @admin.display(description="items", ordering="item_count")
    def request_item_count(self, obj):
        return obj.item_count

    @admin.display(description="Request")
    def stock_request_items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist")
        url = f"{url}?q={obj.request_identifier}"
        context = dict(url=url, label="Request items", title="Go to stock request items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Add")
    def add_stock_request_item(self, obj):
        if obj.item_count > StockRequestItem.objects.filter(request=obj).count():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist"
            url = (
                f"{url}?next={next_url}&stock_request={str(obj.id)}"
                f"&q={str(obj.request_identifier)}"
            )
            context = dict(url=url, label="Add item")
            return render_to_string("edc_pharmacy/stock/items_as_button.html", context=context)
        return None

    @admin.display(description="Request date")
    def request_date(self, obj):
        return to_local(obj.request_datetime).date()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stock_request" and request.GET.get("stock_request"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
