from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import ProductForm
from ...models import Product
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Product, site=edc_pharmacy_admin)
class ProductAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    form = ProductForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "product_identifier",
                        "container_type",
                        "count_per_container",
                        "formulation",
                        "lot",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "product_identifier",
        "container_type",
        "count_per_container",
        "formulation",
        "lot",
        "created",
        "modified",
    )
    list_filter = (
        "formulation",
        "container_type",
    )
    search_fields = (
        "product_identifier",
        "lot__lot_no",
    )
    ordering = (
        "product_identifier",
        "lot__lot_no",
    )
    readonly_fields = ("product_identifier",)

    @admin.display(description="Lot No.", ordering="lot__lot_no")
    def lot(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_lot_changelist")
        url = f"{url}?q={obj.lot.lot_no}"
        context = dict(lot_no=obj.lot.lot_no, url=url)
        return render_to_string("edc_pharmacy/medication/lot_button.html", context)
