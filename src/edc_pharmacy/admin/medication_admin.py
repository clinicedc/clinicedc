from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import MedicationForm
from ..models import Medication
from .model_admin_mixin import ModelAdminMixin


@admin.register(Medication, site=edc_pharmacy_admin)
class MedicationAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = MedicationForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'strength',
                'units',
                'formulation',
                'route',
                'notes',
            )}), audit_fieldset_tuple
    )

    radio_fields = {
        'units': admin.VERTICAL,
        'formulation': admin.VERTICAL,
        'route': admin.VERTICAL
    }

    search_fields = ['name']
    ordering = ['name']
