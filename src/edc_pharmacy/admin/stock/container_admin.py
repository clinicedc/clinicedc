from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin

from ...admin_site import edc_pharmacy_admin
from ...forms import ContainerForm
from ...models import Container
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Container, site=edc_pharmacy_admin)
class ContainerAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Containers"
    show_object_tools = True
    history_list_display = ()
    list_per_page = 20

    form = ContainerForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "name",
                        "display_name",
                        "container_type",
                        "units",
                        "unit_qty_default",
                        "unit_qty_places",
                        "unit_qty_max",
                        "may_order_as",
                        "may_receive_as",
                        "may_repack_as",
                        "may_request_as",
                        "max_items_per_subject",
                        "may_dispense_as",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "name",
        "container_type",
        "unit_qty_max",
        "formatted_units",
        "may_order",
        "may_receive",
        "may_repack",
        "may_request",
        "may_dispense",
        "max_items_per_subject",
        "created",
        "modified",
    )
    list_filter = (
        "container_type",
        "units",
        "may_order_as",
        "may_receive_as",
        "may_repack_as",
        "may_request_as",
        "may_dispense_as",
        "created",
    )
    radio_fields = {"container_type": admin.VERTICAL, "units": admin.VERTICAL}  # noqa: RUF012
    search_fields = (
        "name",
        "display_name",
    )
    ordering = ("display_name",)

    @admin.display(description="Units", ordering="units")
    def formatted_units(self, obj):
        return obj.units.plural_name

    @admin.display(description="order", ordering="may_order_as", boolean=True)
    def may_order(self, obj):
        return obj.may_order_as

    @admin.display(description="receive", ordering="may_receive_as", boolean=True)
    def may_receive(self, obj):
        return obj.may_receive_as

    @admin.display(description="Repack", ordering="may_repack_as", boolean=True)
    def may_repack(self, obj):
        return obj.may_repack_as

    @admin.display(description="request", ordering="may_request_as", boolean=True)
    def may_request(self, obj):
        return obj.may_request_as

    @admin.display(description="dispense", ordering="may_dispense_as", boolean=True)
    def may_dispense(self, obj):
        return obj.may_dispense_as

    def get_readonly_fields(self, request, obj=None):  # noqa: ARG002
        if obj:
            return tuple({*self.readonly_fields, "name"})
        return self.readonly_fields
