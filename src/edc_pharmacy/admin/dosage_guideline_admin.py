from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import DosageGuidelineForm
from ..models import DosageGuideline
from .model_admin_mixin import ModelAdminMixin


@admin.register(DosageGuideline, site=edc_pharmacy_admin)
class DosageGuidelineAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = DosageGuidelineForm

    fieldsets = (
        (None, {
            'fields': (
                'medication_name',
                'dose',
                'dose_per_kg',
                'dose_units',
                'dose_frequency_factor',
                'dose_frequency_units',
                'subject_weight_factor'
            )}),
        audit_fieldset_tuple
    )

    list_display = ['__str__', 'modified', 'user_modified']
    search_fields = ['medication_name']
