from django.contrib import admin

from ..models import IdentifierTracker


class IdentifierTrackerAdmin(admin.ModelAdmin):

    list_display = ('identifier', 'root_number', 'counter', 'created', 'user_created')
    search_fields = ('identifier', 'root_number')
    list_filter = ('created', 'root_number', 'user_created')

admin.site.register(IdentifierTracker, IdentifierTrackerAdmin)
