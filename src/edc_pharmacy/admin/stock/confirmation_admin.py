from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from edc_pharmacy.admin.model_admin_mixin import ModelAdminMixin
from edc_pharmacy.admin.remove_fields_for_blinded_users import (
    remove_fields_for_blinded_users,
)
from edc_pharmacy.admin_site import edc_pharmacy_admin
from edc_pharmacy.forms import ConfirmationForm
from edc_pharmacy.models import Confirmation


@admin.register(Confirmation, site=edc_pharmacy_admin)
class ConfirmationAdmin(ModelAdminMixin, SimpleHistoryAdmin):

    change_list_title = "Pharmacy: Confirmed stock"
    change_form_title = "Pharmacy: Confirmed stock"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = ConfirmationForm

    actions = ["delete_selected"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "confirmation_identifier",
                    "confirmed_datetime",
                    "confirmed_by",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "stock_changelist",
        "confirmed_date",
        "confirmed_by",
    )

    readonly_fields = (
        "confirmed_datetime",
        "confirmed_by",
    )

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    def get_list_filter(self, request):
        fields = super().get_list_filter(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    def get_search_fields(self, request):
        fields = super().get_search_fields(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    @admin.display(description="CONFIRMED #", ordering="confirmation_identifier")
    def identifier(self, obj):
        return obj.confirmation_identifier.split("-")[0]

    @admin.display(description="Confirmed date", ordering="confirmed_datetime")
    def confirmed_date(self, obj):
        return to_local(obj.confirmed_datetime).date()

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=f"{obj.stock.code}", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
