from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import ConfirmationAtLocationItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ConfirmationAtLocationItem, site=edc_pharmacy_admin)
class ConfirmationAtLocationItemAdmin(
    SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin
):
    change_list_title = "Pharmacy: Stock items confirmed at location"
    change_form_title = "Pharmacy: Stock item confirmed at location"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    actions = ("delete_selected",)

    ordering = ("-transfer_confirmation_item_identifier",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_confirmation_item_identifier",
                    "transfer_confirmation_item_datetime",
                    "confirm_at_location",
                    "stock_transfer_item",
                    "confirmed_datetime",
                    "confirmed_by",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "transfer_confirmation_item_date",
        "subject",
        "site",
        "stock_changelist",
        "confirm_at_location_changelist",
        "confirmed_datetime",
        "confirmed_by",
    )

    list_filter = (("transfer_confirmation_item_datetime", DateRangeFilterBuilder()),)

    readonly_fields = (
        "transfer_confirmation_item_identifier",
        "transfer_confirmation_item_datetime",
        "confirm_at_location",
        "stock_transfer_item",
        "confirmed_datetime",
        "confirmed_by",
    )

    search_fields = (
        "pk",
        "confirm_at_location__pk",
        "stock_transfer_item__stock__code",
        "stock_transfer_item__stock__pk",
        "stock_transfer_item__stock__allocation__registered_subject__subject_identifier",
    )

    @admin.display(
        description="CONFIRMATION #", ordering="-transfer_confirmation_item_identifier"
    )
    def identifier(self, obj):
        return obj.transfer_confirmation_item_identifier

    @admin.display(description="Date", ordering="transfer_confirmation_item_datetime")
    def transfer_confirmation_item_date(self, obj):
        return to_local(obj.transfer_confirmation_item_datetime).date()

    @admin.display(description="Site", ordering="confirm_at_location__location__site__id")
    def site(self, obj):
        return obj.confirm_at_location.location.site.id

    @admin.display(
        description="SUBJECT #",
        ordering=(
            "stock_transfer_item__stock__allocation__registered_subject__subject_identifier"
        ),
    )
    def subject(self, obj):
        return obj.stock_transfer_item.stock.allocation.registered_subject.subject_identifier

    @admin.display(
        description="Transfer confirmation",
        ordering="confirm_at_location__transfer_confirmation_identifier",
    )
    def confirm_at_location_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_confirmationatlocation_changelist")
        url = f"{url}?q={obj.confirm_at_location.id}"
        context = dict(
            url=url,
            label=obj.confirm_at_location.transfer_confirmation_identifier,
            title="Go to stock transfer confirmation",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockproxy_changelist")
        url = f"{url}?q={obj.stock_transfer_item.stock.code}"
        context = dict(url=url, label=obj.stock_transfer_item.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
