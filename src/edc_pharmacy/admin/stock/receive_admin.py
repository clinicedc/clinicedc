from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveForm
from ...models import Receive
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Receive, site=edc_pharmacy_admin)
class ReceiveAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = ReceiveForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "receive_datetime",
                    "product",
                    "qty",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "product",
        "qty",
        "warehouse",
        "received_datetime",
        "created",
        "modified",
    )
    list_filter = (
        "product",
        "warehouse",
        "received_datetime",
        "created",
        "modified",
    )
    search_fields = (
        "stock_identifiers",
        "product__product_identifier",
        "product__lot__lot_no",
    )

    ordering = ("received_datetime",)
