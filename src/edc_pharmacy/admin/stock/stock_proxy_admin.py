from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...auth_objects import PHARMACIST_ROLE, PHARMACY_SUPER_ROLE
from ...models import StockProxy
from ..list_filters import (
    ConfirmedAtSiteFilter,
    DispensedFilter,
    StoredAtSiteFilter,
    TransferredListFilter,
)
from .stock_admin import StockAdmin


@admin.register(StockProxy, site=edc_pharmacy_admin)
class StockProxyAdmin(StockAdmin):

    fieldsets = (
        (
            "Stock item",
            {
                "fields": (
                    "stock_identifier",
                    "code",
                    "location",
                )
            },
        ),
        (
            "Quantity",
            {"fields": ("qty_in", "qty_out", "unit_qty_in", "unit_qty_out")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "formatted_code",
        "formatted_transferred",
        "formatted_confirmed_at_site",
        "formatted_stored_at_site",
        "dispensed",
        "stock_request_changelist",
        "stock_transfer_item_changelist",
        "allocation_changelist",
        "dispense_changelist",
        "formulation",
        "qty",
        "container_str",
        "unit_qty",
        "created",
        "modified",
    )
    list_filter = (
        TransferredListFilter,
        ConfirmedAtSiteFilter,
        StoredAtSiteFilter,
        DispensedFilter,
        "product__formulation__description",
        "location__display_name",
        "created",
        "modified",
    )
    search_fields = (
        "stock_identifier",
        "from_stock__stock_identifier",
        "code",
        "from_stock__code",
        "repack_request__id",
        "allocation__registered_subject__subject_identifier",
        "allocation__stock_request_item__id",
        "allocation__stock_request_item__stock_request__id",
        "allocation__id",
        "stocktransferitem__stock_transfer__id",
    )
    readonly_fields = (
        "code",
        "confirmation",
        "container",
        "from_stock",
        "location",
        "repack_request",
        "lot",
        "product",
        "qty_in",
        "qty_out",
        "unit_qty_in",
        "unit_qty_out",
        "receive_item",
        "stock_identifier",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                confirmation__isnull=False,
                allocation__isnull=False,
                container__may_request_as=True,
            )
        )

    def get_list_display_links(self, request, list_display):
        display_links = super().get_list_display_links(request, list_display)
        if not request.user.userprofile.roles.filter(
            name__in=[PHARMACIST_ROLE, PHARMACY_SUPER_ROLE]
        ).exists():
            try:
                display_links.remove("formatted_code")
            except ValueError:
                pass
        return display_links

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
