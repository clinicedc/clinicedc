from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import DispensedItemForm, DispensedItemReadonlyForm
from ..models import DispensedItem
from .model_admin_mixin import ModelAdminMixin


@admin.register(DispensedItem, site=edc_pharmacy_admin)
class DispensedItemAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = DispensedItemForm

    fieldsets = (
        (None, {
            'fields': (
                'prescription_item',
                'dispensed',
                'status',
                'dispensed_datetime',
            )}), audit_fieldset_tuple
    )

    list_display = ['subject_identifier',
                    'prescription_item', 'dispensed_date', 'dispensed']
    list_filter = ['dispensed_datetime', 'status']
    search_fields = ['prescription__subject_identifier',
                     'prescription_item__medication__name']
    ordering = ['dispensed_datetime']


class DispensedItemInlineAdmin(admin.TabularInline):

    form = DispensedItemReadonlyForm
    model = DispensedItem

    fields = [
        'dispensed',
        'status',
        'dispensed_datetime',
    ]
    ordering = ['dispensed_datetime']
    extra = 0
