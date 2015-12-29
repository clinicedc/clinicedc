from django.contrib import admin
from collections import OrderedDict

from edc_base.modeladmin.admin import BaseModelAdmin
from edc.export.actions import export_as_csv_action

from ..models import Order

from ..actions import refresh_order_status


class OrderAdmin(BaseModelAdmin):
    date_hierarchy = 'order_datetime'
    list_display = ("order_identifier", "receive_identifier", "to_receive", "to_result", "subject_identifier",
                    "panel", "order_datetime", 'status', 'import_datetime')
    search_fields = ('aliquot__receive__registered_subject__subject_identifier', "order_identifier",
                     "aliquot__receive__receive_identifier")
    list_filter = ('status', 'import_datetime', 'aliquot__aliquot_condition', 'panel__edc_name')
    list_per_page = 15
#     actions = [refresh_order_status, ]
    actions = [
        export_as_csv_action("CSV Export: adds subject_identifier, gender, dob",
            fields=[],
            delimiter=',',
            exclude=['id', 'revision',],
            extra_fields=OrderedDict(
                {'gender': 'aliquot__receive__registered_subject__gender',
                'dob': 'aliquot__receive__registered_subject__dob'}),
                ),
        refresh_order_status,]

    def get_readonly_fields(self, request, obj):
        return ['aliquot', 'status', 'order_datetime', 'comment']
admin.site.register(Order, OrderAdmin)
