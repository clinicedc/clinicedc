from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import PrescriptionForm
from ..models import Prescription
from .dispensed_item_admin import DispensedItemInlineAdmin
from .model_admin_mixin import ModelAdminMixin
from .prescription_item_admin import PrescriptionItemInlineAdmin


@admin.register(Prescription, site=edc_pharmacy_admin)
class PrescriptionAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = PrescriptionForm

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'report_datetime',
                'clinician_initials',
                'notes',
            )}),
        ('Randomization', {
            'classes': ('collapse',),
            'fields': (
                'rando_sid',
                'rando_arm',
                'weight_in_kgs',
            )}),
        audit_fieldset_tuple
    )

    inlines = [PrescriptionItemInlineAdmin, DispensedItemInlineAdmin]

    list_display = ['subject_identifier', '__str__',
                    'prescription_date', 'weight_in_kgs']
    search_fields = ['subject_identifier', 'rando_sid']
