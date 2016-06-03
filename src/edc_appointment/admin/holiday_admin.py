from django.contrib import admin

from .base_model_admin import BaseModelAdmin
from edc_base.modeladmin.admin import BaseTabularInline

from ..models import Holiday


class HolidayAdmin(BaseModelAdmin):
    pass
admin.site.register(Holiday, HolidayAdmin)


class HolidayInlineAdmin(BaseTabularInline):
    model = Holiday
    extra = 0
