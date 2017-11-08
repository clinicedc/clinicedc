from django.contrib import admin

from .models import SubjectLocator


@admin.register(SubjectLocator)
class SubjectLocatorAdmin(admin.ModelAdmin):
    pass
