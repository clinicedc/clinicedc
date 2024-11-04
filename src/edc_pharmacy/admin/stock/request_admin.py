from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import RequestForm
from ...models import Request, RequestItem
from ..actions import create_request_items_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Request, site=edc_pharmacy_admin)
class RequestAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Request for stock"
    show_object_tools = True
    show_cancel = True
    autocomplete_fields = ["container", "formulation", "site_proxy"]
    form = RequestForm

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
        "request_id",
        "request_date",
        "site_proxy",
        "formulation",
        "container",
        "per_subject",
        "request_item_count",
        "add_request_item",
        "items",
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
    def request_id(self, obj):
        return obj.request_identifier

    @admin.display(description="Per", ordering="containers_per_subject")
    def per_subject(self, obj):
        return obj.containers_per_subject

    @admin.display(description="items", ordering="item_count")
    def request_item_count(self, obj):
        return obj.item_count

    @admin.display(description="Request")
    def items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_requestitem_changelist")
        url = f"{url}?q={obj.request_identifier}"
        context = dict(url=url, label="Request items", title="Go to request items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Add")
    def add_request_item(self, obj):
        if obj.item_count > RequestItem.objects.filter(request=obj).count():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_requestitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_request_changelist"
            url = (
                f"{url}?next={next_url}&request={str(obj.id)}&q={str(obj.request_identifier)}"
            )
            context = dict(url=url, label="Add item")
            return render_to_string("edc_pharmacy/stock/items_as_button.html", context=context)
        return None

    @admin.display(description="Request date")
    def request_date(self, obj):
        return to_local(obj.request_datetime).date()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "request" and request.GET.get("request"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
