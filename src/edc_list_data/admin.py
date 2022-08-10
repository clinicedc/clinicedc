from typing import Tuple

from django.contrib import admin


class ListModelAdminMixin(admin.ModelAdmin):

    ordering: Tuple[str, ...] = ("display_index", "display_name")

    list_display: Tuple[str, ...] = ("display_name", "name", "display_index")

    search_fields: Tuple[str, ...] = ("display_name", "name")
