from django.contrib import admin
from edc_fieldsets import Fieldset
from edc_model_admin import audit_fieldset_tuple, audit_fields

from ..admin_site import edc_lab_admin
from ..forms import AliquotForm
from ..models import Aliquot
from .base_model_admin import BaseModelAdmin


aliquot_identifiers_fields = (
    'subject_identifier',
    'requisition_identifier',
    'parent_identifier',
    'identifier_prefix')

aliquot_identifiers_fieldset_tuple = Fieldset(
    *aliquot_identifiers_fields,
    section='Identifiers').fieldset


@admin.register(Aliquot, site=edc_lab_admin)
class AliquotAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = AliquotForm

    fieldsets = (
        (None, {
            'fields': (
                'aliquot_identifier',
                'aliquot_datetime',
                'aliquot_type',
                'numeric_code',
                'alpha_code',
                'condition',
            )}),
        aliquot_identifiers_fieldset_tuple,
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return (super().get_readonly_fields(request, obj=obj)
                + audit_fields
                + aliquot_identifiers_fields)

    list_display = ('aliquot_identifier', 'subject_identifier',
                    'aliquot_datetime', 'aliquot_type', 'condition')

    list_filter = ('aliquot_datetime', 'aliquot_type', 'condition')

    search_fields = ('aliquot_identifier', 'subject_identifier', )

    radio_fields = {
        'condition': admin.VERTICAL}


class AliquotInlineAdmin(admin.TabularInline):
    model = Aliquot
    extra = 0
    fields = ('aliquot_identifier', )
