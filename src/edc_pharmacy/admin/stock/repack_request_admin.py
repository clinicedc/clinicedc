from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import RepackRequestForm
from ...models import RepackRequest
from ..actions import process_repack_request_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(RepackRequest, site=edc_pharmacy_admin)
class RequestRepackAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Repackage request"
    show_object_tools = True
    show_cancel = True
    autocomplete_fields = ["container", "label_specification"]
    form = RepackRequestForm
    actions = [process_repack_request_action]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "repack_identifier",
                    "repack_datetime",
                    "from_stock",
                    "container",
                    "qty",
                    "label_specification",
                )
            },
        ),
        (
            "Section B: Confirm stock after labelling",
            {
                "fields": (
                    "stock_count",
                    "stock_identifiers",
                    "confirmed_stock_identifiers",
                    "unconfirmed_stock_identifiers",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "repack_identifier",
        "repack_datetime",
        "from_stock",
        "container",
        # "product",
        "qty",
        "processed",
        "stock_changelist",
    )

    search_fields = ("id", "container__name")
    readonly_fields = ("confirmed_stock_identifiers", "unconfirmed_stock_identifiers")

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
