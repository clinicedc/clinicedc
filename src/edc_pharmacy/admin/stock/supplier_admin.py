from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin

from ...admin_site import edc_pharmacy_admin
from ...forms import SupplierForm
from ...models import Supplier
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Supplier, site=edc_pharmacy_admin)
class SupplierAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Suppliers"
    change_form_title = "Pharmacy: Supplier"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True

    form = SupplierForm
    ordering = ("name",)

    fieldsets = (
        (
            None,
            {"fields": (["name", "contact"])},
        ),
        (
            "Address",
            {
                "fields": (
                    [
                        "address_one",
                        "address_two",
                        "city",
                        "postal_code",
                        "state",
                        "country",
                    ]
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    [
                        "email",
                        "email_alternative",
                        "telephone",
                        "telephone_alternative",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "name",
        "contact",
        "created",
        "modified",
    )
    list_filter = ("country",)
    search_fields = ("id", "supplier_identifier", "name", "contact")

    @admin.display(description="SUPPLIER #", ordering="-supplier_identifier")
    def identifier(self, obj):
        return obj.supplier_identifier
