from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    StackedInlineModelAdminMixin,
    TemplatesModelAdminMixin,
)

from ...admin_site import meta_pharmacy_admin
from ...forms import StockTransferForm, StockTransferItemsForm
from ...models import StockTransfer, StockTransferItems
from ..actions import prepare_label_data, print_label_sheet_from_batch


class StockTransferItemsInlineAdmin(StackedInlineModelAdminMixin, admin.StackedInline):
    model = StockTransferItems
    form = StockTransferItemsForm
    extra = 1
    fields = [
        "bottle_count",
        "barcodes",
    ]


@admin.register(StockTransfer, site=meta_pharmacy_admin)
class StockTransferAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminAuditFieldsMixin,
    admin.ModelAdmin,
):
    show_object_tools: bool = True

    form = StockTransferForm

    actions = [print_label_sheet_from_batch, prepare_label_data]

    inlines = [StockTransferItemsInlineAdmin]

    fieldsets = (
        ("Section One", {"fields": ("stock_transfer_identifier", "lot", "site", "status")}),
        # (
        #     "Section Two: Post-label printing",
        #     {
        #         "description": _(
        #             "Complete this section ONLY after printing the labels "
        #             "in this batch and preparing and labeling "
        #             "all bottles in this batch. "
        #             "Scan each bottle's barcode into the box below. The bottle "
        #             "count should match the number "
        #             "barcodes scanned."
        #         ),
        #         "fields": ("bottle_count", "barcodes"),
        #     },
        # ),
        audit_fieldset_tuple,
    )

    list_display = (
        "stock_transfer_identifier",
        "lot",
        "site",
        "label_data",
        "status",
        "created",
    )
    list_filter = ("status", "created", "site_id")
    readonly_fields = ("stock_transfer_identifier", "created")
    search_fields = ("stock_transfer_identifier", "lot__lot_no")

    @admin.display(description="Label data", ordering="stock_transfer_identifier")
    def label_data(self, obj):
        url = reverse("meta_pharmacy_admin:meta_pharmacy_labeldata_changelist")
        url = f"{url}?q={obj.batch}"
        return format_html(f'<A href="{url}">Label Data</A>')
