from django.contrib import admin

from edc_model_admin.mixins import TemplatesModelAdminMixin


class ListModelAdminMixin(TemplatesModelAdminMixin, admin.ModelAdmin):
    ordering = ("display_index", "display_name")

    list_display = ("display_name", "name", "display_index")

    search_fields = ("display_name", "name")
