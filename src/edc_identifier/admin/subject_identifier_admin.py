from django.contrib import admin

from ..models import SubjectIdentifier


class SubjectIdentifierAdmin(admin.ModelAdmin):

    list_display = ('identifier', 'created', 'user_created', 'hostname_created')
    search_fields = ('identifier', )
    list_filter = ('created', 'user_created')

admin.site.register(SubjectIdentifier, SubjectIdentifierAdmin)
