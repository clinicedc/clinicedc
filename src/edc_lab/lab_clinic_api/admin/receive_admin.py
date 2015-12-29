from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import Receive


class ReceiveAdmin(BaseModelAdmin):

    date_hierarchy = 'receive_datetime'

    list_display = ('registered_subject', 'to_order', "receive_identifier", "receive_datetime", "requisition_identifier", "drawn_datetime",)

    search_fields = ('registered_subject__subject_identifier', "receive_identifier", "requisition_identifier",)

    list_filter = ("receive_datetime", "drawn_datetime", 'import_datetime', )

    list_per_page = 15

    def get_readonly_fields(self, request, obj):
        return ['receive_identifier'] + [field.name for field in obj._meta.fields if field.editable]

admin.site.register(Receive, ReceiveAdmin)
