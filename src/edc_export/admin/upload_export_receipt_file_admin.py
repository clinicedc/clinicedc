from django.contrib import admin

from ..admin_site import edc_export_admin
from ..models import UploadExportReceiptFile


@admin.register(UploadExportReceiptFile, site=edc_export_admin)
class UploadExportReceiptFileAdmin(admin.ModelAdmin):

    date_hierarchy = 'created'

    list_display = (
        'file_name', 'accepted', 'duplicate',
        'total', 'errors', 'created', 'user_created',
        'hostname_created')

    list_filter = ('created', 'hostname_created')
