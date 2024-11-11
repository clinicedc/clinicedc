from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestForm
from ...models import StockRequest, StockRequestItem
from ..actions import (
    allocate_stock_to_subject,
    create_stock_request_items_action,
    go_to_allocated_stock,
    go_to_stock,
)
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockRequest, site=edc_pharmacy_admin)
class StockRequestAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Request for stock"
    show_object_tools = True
    show_cancel = True
    autocomplete_fields = ["container", "formulation", "location"]
    form = StockRequestForm

    actions = [
        create_stock_request_items_action,
        allocate_stock_to_subject,
        go_to_allocated_stock,
        go_to_stock,
    ]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "request_identifier",
                    "request_datetime",
                    "location",
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
            "Section D: Customize this request",
            {"fields": ("subject_identifiers", "excluded_subject_identifiers")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "stock_request_id",
        "request_date",
        "location",
        "formulation",
        "per_subject",
        "container",
        "stock_request_items",
        "status",
    )

    list_filter = (
        "request_datetime",
        "status",
        "formulation",
        "container",
        "location",
    )

    radio_fields = {
        "status": admin.VERTICAL,
    }

    search_fields = ["id", "request_identifier"]

    readonly_fields = ["item_count"]

    @admin.display(description="Request #", ordering="request_identifier")
    def stock_request_id(self, obj):
        return obj.request_identifier

    @admin.display(description="QTY", ordering="containers_per_subject")
    def per_subject(self, obj):
        return obj.containers_per_subject

    @admin.display(description="items", ordering="item_count")
    def request_item_count(self, obj):
        return obj.item_count

    @admin.display(description="Request items")
    def stock_request_items(self, obj):
        count = StockRequestItem.objects.filter(stock_request=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist")
        url = f"{url}?q={obj.request_identifier}"
        context = dict(
            url=url, label=f"Request items ({count})", title="Go to stock request items"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    # @admin.display(description="Add")
    # def add_stock_request_item(self, obj):
    #     if obj.item_count > StockRequestItem.objects.filter(stock_request=obj).count():
    #         url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_add")
    #         next_url = "edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist"
    #         url = (
    #             f"{url}?next={next_url}&stock_request={str(obj.id)}"
    #             f"&q={str(obj.request_identifier)}"
    #         )
    #         context = dict(url=url, label="Add item")
    #         return render_to_string(
    #             "edc_pharmacy/stock/items_as_button.html", context=context)
    #     return None

    @admin.display(description="Request date")
    def request_date(self, obj):
        return to_local(obj.request_datetime).date()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stock_request" and request.GET.get("stock_request"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        messages.add_message(
            request,
            messages.SUCCESS,
            (
                "Your next step is to prepare the items for "
                "this stock request. Select from actions below."
            ),
        )
        obj.save()
