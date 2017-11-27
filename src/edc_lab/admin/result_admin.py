from django.contrib import admin
from edc_model_admin import TabularInlineMixin

from ..admin_site import edc_lab_admin
from ..models import Result, ResultItem
from .base_model_admin import BaseModelAdmin


@admin.register(ResultItem, site=edc_lab_admin)
class ResultItemAdmin(BaseModelAdmin, admin.ModelAdmin):
    pass


class ResultItemInlineAdmin(TabularInlineMixin, admin.TabularInline):
    model = ResultItem


@admin.register(Result, site=edc_lab_admin)
class ResultAdmin(BaseModelAdmin, admin.ModelAdmin):
    inlines = [ResultItemInlineAdmin]
