from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...models import ConfirmationAtSite
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ConfirmationAtSite, site=edc_pharmacy_admin)
class ConfirmationAtSiteAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock confirmations at site"
    change_form_title = "Pharmacy: Stock confirmation at site"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    ordering = ("-transfer_confirmation_identifier",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_confirmation_identifier",
                    "transfer_confirmation_datetime",
                    "stock_transfer",
                    "location",
                    "comments",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "transfer_confirmation_date",
        "location",
        "confirmation_at_site_item_changelist",
        "stock_transfer_changelist",
    )

    list_filter = (
        "location",
        ("transfer_confirmation_datetime", DateRangeFilterBuilder()),
    )

    readonly_fields = (
        "transfer_confirmation_identifier",
        "transfer_confirmation_datetime",
        "stock_transfer",
        "location",
    )

    search_fields = (
        "pk",
        "stock_transfer__pk",
        "confirmationatsiteitem__stock__code",
        (
            "confirmationatsiteitem__stock__allocation__"
            "registered_subject__subject_identifier"
        ),
    )

    @admin.display(description="CONFIRMATION #", ordering="-transfer_confirmation_identifier")
    def identifier(self, obj):
        return obj.transfer_confirmation_identifier.split("-")[0]

    @admin.display(description="Date", ordering="transfer_confirmation_datetime")
    def transfer_confirmation_date(self, obj):
        return to_local(obj.transfer_confirmation_datetime).date()

    @admin.display(description="Confirmed items")
    def confirmation_at_site_item_changelist(self, obj):
        item_count = obj.confirmationatsiteitem_set.all().count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_confirmationatsiteitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(
            url=url,
            label=_("Confirmed items (%(item_count)s)") % {"item_count": item_count},
            title="Go to stock transfer confirmation items",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(
        description="Stock Transfer", ordering="stock_transfer__transfer_identifier"
    )
    def stock_transfer_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransfer_changelist")
        url = f"{url}?q={obj.stock_transfer.id}"
        context = dict(
            url=url,
            label=(
                f"{obj.stock_transfer.transfer_identifier} ({obj.stock_transfer.item_count})"
            ),
            title="Go to stock transfer",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
