from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import ContainerForm
from ...models import Container
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Container, site=edc_pharmacy_admin)
class ContainerAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Containers"
    show_object_tools = True

    form = ContainerForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "name",
                        "container_type",
                        "units",
                        "qty",
                        "may_order_as",
                        "may_receive_as",
                        "may_request_as",
                    ]
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "name",
        "container_type",
        "units",
        "qty",
        "may_order",
        "may_receive",
        "may_request",
        "created",
        "modified",
    )
    list_filter = (
        "container_type",
        "units",
        "may_order_as",
        "may_receive_as",
        "may_request_as",
        "created",
    )
    radio_fields = {"container_type": admin.VERTICAL, "units": admin.VERTICAL}
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="order", ordering="may_order_as")
    def may_order(self, obj):
        return obj.may_order_as

    @admin.display(description="receive", ordering="may_receive_as")
    def may_receive(self, obj):
        return obj.may_receive_as

    @admin.display(description="request", ordering="may_request_as")
    def may_request(self, obj):
        return obj.may_request_as
