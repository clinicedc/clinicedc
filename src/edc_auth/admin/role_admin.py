from django.contrib import admin

from ..models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    fieldsets = ((None, ({"fields": ("display_name", "name", "display_index", "groups")})),)

    list_display = ["display_name", "name", "display_index"]

    filter_horizontal = ("groups",)

    search_fields = ("display_name", "name", "groups__name")

    ordering = ("display_index", "display_name")
