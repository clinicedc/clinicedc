from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin, BaseTabularInline

from ..models import AttachedModel


class AttachedModelInlineAdmin(BaseTabularInline):
    model = AttachedModel
    extra = 1


class AttachedModelAdmin(BaseModelAdmin):
    list_display = ('content_type_map', 'consent_catalogue', 'is_active', 'created')
    list_filter = ('consent_catalogue', 'is_active', 'created')
    search_fields = ('content_type_map__model', 'content_type_map__app_label', 'content_type_map__name',)
admin.site.register(AttachedModel, AttachedModelAdmin)
