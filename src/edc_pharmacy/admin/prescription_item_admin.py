from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import PrescriptionItemForm
from ..models import PrescriptionItem
from .model_admin_mixin import ModelAdminMixin


@admin.register(PrescriptionItem, site=edc_pharmacy_admin)
class PrescriptionItemAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = PrescriptionItemForm

    model = PrescriptionItem

    fieldsets = (
        (None, {
            'fields': (
                'prescription',
                'medication',
                'dosage_guideline',
                'calculate_dose',
                'dose',
                'frequency',
                'frequency_units',
                'start_date',
                'end_date',
                'notes',
            )}),
        ('Verification', {
            'classes': ('collapse',),
            'fields': (
                'verified',
                'verified_datetime',
            )}),
        ('Calculations', {
            'classes': ('collapse',),
            'fields': (
                'total',
                'remaining'
            )}),
        audit_fieldset_tuple)

    list_display = ('subject_identifier', '__str__', 'duration', 'total',
                    'remaining', 'verified', 'verified_datetime')
    list_filter = ('start_date', 'end_date', )
    search_fields = ['prescription__subject_identifier', 'medication__name']
    ordering = ['medication__name']


class PrescriptionItemInlineAdmin(admin.StackedInline):

    form = PrescriptionItemForm

    model = PrescriptionItem

    fields = [
        'medication',
        'dosage_guideline',
        'calculate_dose',
        'dose',
        'frequency',
        'frequency_units',
        'start_date',
        'end_date']

    search_fields = ['medication__name']
    ordering = ['medication__name']
    extra = 0
