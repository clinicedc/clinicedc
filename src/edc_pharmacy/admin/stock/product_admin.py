from django.contrib import admin
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
                        "formulation",
                        "assignment",
                        "name",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "name",
        "formulation",
        "assignment",
        "identifier",
        "created",
        "modified",
    )
    list_filter = (
        "formulation",
        "assignment",
    )
    search_fields = (
        "product_identifier",
        "lot__lot_no",
    )
    ordering = ("product_identifier",)
    readonly_fields = ("product_identifier",)

    @admin.display(description="Product identifier", ordering="product_identifier")
    def identifier(self, obj):
        return obj.product_identifier.split("-")[0]
