from django.contrib import admin

from edc_model_admin.mixins import TemplatesModelAdminMixin


class ListModelAdminMixin(TemplatesModelAdminMixin, admin.ModelAdmin):
    ordering: tuple[str, ...] = ("display_index", "display_name")

    list_display: tuple[str, ...] = ("display_name", "name", "display_index")

    search_fields: tuple[str, ...] = ("display_name", "name")
