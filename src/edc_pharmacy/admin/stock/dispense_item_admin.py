from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import DispenseItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(DispenseItem, site=edc_pharmacy_admin)
class DispenseItemAdmin(SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Dispense items"
    change_form_title = "Pharmacy: Dispense item"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    fieldsets = (
        (
            "Section A: Repack",
            {
                "fields": (
                    "dispense_item_identifier",
                    "dispense_item_datetime",
                    "dispense",
                    "stock",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "subject",
        "location",
        "dispense_date",
        "dispense_changelist",
        "stock_changelist",
        "dispensed_by",
    )

    search_fields = (
        "id",
        "dispense__id",
        "stock__code",
        "dispense__rx__subject_identifier",
    )

    readonly_fields = (
        "dispense_item_identifier",
        "dispense_item_datetime",
        "dispense",
        "stock",
    )

    @admin.display(description="Dispense #", ordering="-dispense_item_identifier")
    def identifier(self, obj):
        return obj.dispense_item_identifier

    @admin.display(
        description="Subject #",
        ordering="dispense__rx__registered_subject__subject_identifier",
    )
    def subject(self, obj):
        return obj.dispense.rx.registered_subject.subject_identifier

    @admin.display(
        description="Location",
        ordering="dispense__location",
    )
    def location(self, obj):
        return obj.dispense.location

    @admin.display(
        description="dispensed by",
        ordering="dispense__dispensed_by",
    )
    def dispensed_by(self, obj):
        return obj.dispense.dispensed_by

    @admin.display(description="item date", ordering="dispense_item_datetime")
    def dispense_date(self, obj):
        return to_local(obj.dispense_item_datetime).date()

    @admin.display(description="DISPENSE #")
    def dispense_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_dispense_changelist")
        url = f"{url}?q={obj.dispense.id}"
        context = dict(url=url, label=obj.dispense.dispense_identifier, title="Go to dispense")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockproxy_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
