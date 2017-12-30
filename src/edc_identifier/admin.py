from django.contrib import admin

from .admin_site import edc_identifier_admin
from .models import IdentifierModel


@admin.register(IdentifierModel, site=edc_identifier_admin)
class IdentifierModelAdmin(admin.ModelAdmin):

    list_display = (
        'identifier', 'name', 'identifier_type', 'site', 'linked_identifier', 'created',
        'user_created', 'hostname_created')
    list_filter = ('identifier_type', 'name', 'site',
                   'device_id', 'created', 'user_created')
    search_fields = ('identifier', )

    def get_readonly_fields(self, request, obj=None):
        return self.fields
