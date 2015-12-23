from django.contrib import admin

from ..models import Sequence


class SequenceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'device_id', 'created', 'user_created', 'hostname_created')
    list_filter = ('created', 'hostname_created', 'user_created', 'device_id',)
admin.site.register(Sequence, SequenceAdmin)
