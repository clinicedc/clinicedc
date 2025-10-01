from django.contrib import admin
from django.utils.safestring import mark_safe

from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_auth_admin
from ..models import Role


@admin.register(Role, site=edc_auth_admin)
class RoleAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    fieldsets = ((None, ({"fields": ("display_name", "name", "display_index", "groups")})),)

    list_display_links = ("display_name", "group_list")

    list_display = ("display_name", "name", "group_list")

    filter_horizontal = ("groups",)

    search_fields = ("display_name", "name", "groups__name")

    ordering = ("display_index", "display_name")

    list_filter = ("groups__name",)

    @staticmethod
    def group_list(obj=None) -> str:
        group_names = [group.name for group in obj.groups.all()]
        group_names.sort()
        return mark_safe("<BR>".join(group_names))  # noqa: S308
