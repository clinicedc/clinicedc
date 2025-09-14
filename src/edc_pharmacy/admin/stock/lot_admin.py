from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from edc_model_admin.history import SimpleHistoryAdmin
from edc_randomization.blinding import user_is_blinded_from_request

from ...admin_site import edc_pharmacy_admin
from ...forms import LotForm
from ...models import Lot
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


@admin.register(Lot, site=edc_pharmacy_admin)
class LotAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Batches"
    change_form_title = "Pharmacy: Batch"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = LotForm

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "lot_no",
                    "product",
                    "manufactured_date",
                    "processed_until_date",
                    "expiration_date",
                ]
            },
        ),
        (
            "Assignment",
            {
                "fields": [
                    "assignment",
                ]
            },
        ),
        (
            "Details",
            {
                "fields": [
                    "country_of_origin",
                    "manufactured_by",
                    "storage_conditions",
                ]
            },
        ),
        (
            "Reference",
            {
                "fields": [
                    "reference",
                    "comment",
                ]
            },
        ),
        audit_fieldset_tuple,
    )

    list_filter: tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "product",
        "assignment",
        "reference",
        "created",
        "modified",
    )

    list_display: tuple[str, ...] = (
        "lot_no",
        "expiration_date",
        "product",
        "assignment",
        "reference",
        "created",
        "modified",
    )
    radio_fields: tuple[str, ...] = {"assignment": admin.VERTICAL}

    search_fields: tuple[str, ...] = ("lot_no",)

    ordering: tuple[str, ...] = ("-expiration_date",)

    def get_readonly_fields(self, request, obj=None):
        # if obj:
        #     return self.readonly_fields + ("lot_no", "product", "assignment")
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if obj and user_is_blinded_from_request(request):
            return (
                (
                    None,
                    {
                        "fields": [
                            "lot_no",
                            "expiration_date",
                            "product",
                        ]
                    },
                ),
                audit_fieldset_tuple,
            )
        return self.fieldsets

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
