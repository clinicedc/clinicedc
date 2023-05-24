from typing import Tuple

from django.contrib import admin
from django.utils.html import format_html
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_auth_admin
from ..models import Role


@admin.register(Role, site=edc_auth_admin)
class RoleAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    fieldsets = ((None, ({"fields": ("display_name", "name", "display_index", "groups")})),)

    list_display_links: Tuple[str, ...] = ("display_name", "group_list")

    list_display: Tuple[str, ...] = ("display_name", "name", "group_list")

    filter_horizontal: Tuple[str, ...] = ("groups",)

    search_fields: Tuple[str, ...] = ("display_name", "name", "groups__name")

    ordering: Tuple[str, ...] = ("display_index", "display_name")

    list_filter = ("groups__name",)

    @staticmethod
    def group_list(obj=None) -> str:
        group_names = []
        for group in obj.groups.all():
            group_names.append(group.name)
        group_names.sort()
        return format_html("<BR>".join(group_names))
