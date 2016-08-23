from django.contrib import admin

from .base_model_admin import BaseModelAdmin

from ..models import TestCode, TestCodeGroup


class TestCodeAdmin(BaseModelAdmin):
    list_display = ('code', 'name', 'edc_code', 'edc_name')
    list_filter = ('test_code_group', )
    search_fields = ('code', 'name', 'edc_code', 'edc_name',
                     'test_code_group__code', 'test_code_group__name')
admin.site.register(TestCode, TestCodeAdmin)


class TestCodeGroupAdmin(BaseModelAdmin):
    list_display = ('code', 'name')
admin.site.register(TestCodeGroup, TestCodeGroupAdmin)
