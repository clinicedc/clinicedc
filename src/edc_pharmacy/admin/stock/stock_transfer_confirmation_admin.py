from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...models import StockTransferConfirmation
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockTransferConfirmation, site=edc_pharmacy_admin)
class StockTransferConfirmationAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Stock transfer confirmations"
    change_form_title = "Pharmacy: Stock transfer confirmation"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    ordering = ("confirmed_datetime",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_confirmation_identifier",
                    "stock",
                    "confirmed_datetime",
                    "confirmed_by",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "subject",
        "stock_changelist",
        "confirmed_datetime",
        "confirmed_by",
    )

    readonly_fields = (
        "transfer_confirmation_identifier",
        "stock",
        "confirmed_datetime",
        "confirmed_by",
    )

    @admin.display(description="CONFIRMATION #", ordering="-transfer_confirmation_identifier")
    def identifier(self, obj):
        return obj.transfer_confirmation_identifier.split("-")[0]

    @admin.display(
        description="SUBJECT #",
        ordering="stock__allocation__registered_subject__subject_identifier",
    )
    def subject(self, obj):
        return obj.stock.allocation.registered_subject.subject_identifier

    @admin.display(description="Stock", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
