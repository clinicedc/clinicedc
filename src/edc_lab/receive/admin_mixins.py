from django.contrib import admin


class ReceiveModelAdminMixin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # In edit mode
            return ('receive_identifier',) + self.readonly_fields
        else:
            return self.readonly_fields

    list_display = ('receive_identifier', 'drawn_datetime', 'receive_datetime')
    search_fields = ('receive_identifier', 'patient__subject_identifier')
    list_filter = ('drawn_datetime', 'receive_datetime')
    list_per_page = 15
    date_hierarchy = 'drawn_datetime'
