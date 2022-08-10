from typing import Tuple

from django.contrib import admin

from ..models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    fieldsets = ((None, ({"fields": ("display_name", "name", "display_index", "groups")})),)

    list_display: Tuple[str, ...] = ("display_name", "name", "display_index")

    filter_horizontal: Tuple[str, ...] = ("groups",)

    search_fields: Tuple[str, ...] = ("display_name", "name", "groups__name")

    ordering: Tuple[str, ...] = ("display_index", "display_name")
