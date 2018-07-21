from django.contrib import admin

from ..admin_site import edc_pdutils_admin
from ..models import DataRequest


@admin.register(DataRequest, site=edc_pdutils_admin)
class DataRequestAdmin(admin.ModelAdmin):

    fields = ('requested', 'export_format', 'decrypt', )

    list_display = ('archive_filename', 'user_created', 'created')
