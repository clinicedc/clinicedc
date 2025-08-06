from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...forms import DispenseForm
from ...models import Dispense
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Dispense, site=edc_pharmacy_admin)
class DispenseAdmin(SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Dispense"
    change_form_title = "Pharmacy: Dispense"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = DispenseForm

    fieldsets = (
        (
            "Section A: Dispense",
            {
                "fields": (
                    "dispense_identifier",
                    "dispense_datetime",
                    "location",
                    "rx",
                    "dispensed_by",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "dispense_date",
        "subject",
        "formulation",
        "location",
        "dispense_item_changelist",
        "stock_changelist",
    )

    search_fields = (
        "id",
        "rx__subject_identifier",
        "dispenseitem__stock__code",
    )

    list_filter = (
        ("dispense_datetime", DateRangeFilterBuilder()),
        "location__display_name",
    )

    readonly_fields = (
        "dispense_identifier",
        "dispense_datetime",
        "rx",
        "location",
        "dispensed_by",
    )

    @admin.display(description="Dispense #", ordering="-dispense_identifier")
    def identifier(self, obj):
        return obj.dispense_identifier

    @admin.display(
        description="Subject #", ordering="rx__registered_subject__subject_identifier"
    )
    def subject(self, obj):
        return obj.rx.registered_subject.subject_identifier

    @admin.display(description="Formulation")
    def formulation(self, obj):
        return "<BR>".join([o.display_name for o in obj.rx.medications.all()])

    @admin.display(description="Dispense date", ordering="dispense_datetime")
    def dispense_date(self, obj):
        return to_local(obj.dispense_datetime).date()

    @admin.display(description="Dispense items")
    def dispense_item_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_dispenseitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Dispense items", title="Go to items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
