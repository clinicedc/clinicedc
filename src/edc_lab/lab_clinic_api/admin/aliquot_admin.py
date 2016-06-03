from django.contrib import admin

from .base_model_admin import BaseModelAdmin

from lis.labeling.actions import print_aliquot_label

from ..models import Aliquot

@admin.register(Aliquot)
class AliquotAdmin(BaseModelAdmin):

    actions = [print_aliquot_label]

    list_display = ("aliquot_identifier", 'subject_identifier',
                    'to_receive', 'drawn', "aliquot_type", 'aliquot_condition',)

    search_fields = ('aliquot_identifier', 'receive__receive_identifier',
                     'receive__registered_subject__subject_identifier')

    list_filter = ('aliquot_type', 'aliquot_condition',)

    list_per_page = 15

#admin.site.register(Aliquot, AliquotAdmin)
