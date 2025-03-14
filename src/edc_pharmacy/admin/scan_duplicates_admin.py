from django.contrib import admin
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_pharmacy_admin
from ..models import ScanDuplicates


@admin.register(ScanDuplicates, site=edc_pharmacy_admin)
class ScanDuplicatesAdmin(SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Scan duplicates"
    change_form_title = "Pharmacy: Scan duplicates"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    fieldsets = (
        (
            None,
            {"fields": ("identifier",)},
        ),
        audit_fieldset_tuple,
    )

    list_display = ("identifier",)

    search_fields = ("id", "identifier")
