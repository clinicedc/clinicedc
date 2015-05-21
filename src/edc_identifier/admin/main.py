from django.contrib import admin

from ..models import SubjectIdentifier, IdentifierTracker, Sequence


class SubjectIdentifierAdmin(admin.ModelAdmin):

    list_display = ('identifier', 'created', 'user_created', 'hostname_created')
    search_fields = ('identifier', )
    list_filter = ('created', 'user_created')

admin.site.register(SubjectIdentifier, SubjectIdentifierAdmin)


class IdentifierTrackerAdmin(admin.ModelAdmin):

    list_display = ('identifier', 'root_number', 'counter', 'created', 'user_created')
    search_fields = ('identifier', 'root_number')
    list_filter = ('created', 'root_number', 'user_created')

admin.site.register(IdentifierTracker, IdentifierTrackerAdmin)


class SequenceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'device_id', 'created', 'user_created', 'hostname_created')
    list_filter = ('created', 'hostname_created', 'user_created', 'device_id',)
admin.site.register(Sequence, SequenceAdmin)
