from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from edc_model_admin.mixins import TemplatesModelAdminMixin

from edc_auth.admin_site import edc_auth_admin

admin.site.unregister(Group)


@admin.register(Group, site=edc_auth_admin)
class GroupAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    ordering = ("name",)

    list_display_links = ("name", "codenames")

    list_display = ("name", "codenames")

    list_filter = (
        "name",
        "permissions__codename",
    )

    search_fields = (
        "name",
        "permissions__codename",
    )

    @staticmethod
    def codenames(obj=None) -> str:
        codenames = []
        for permission in obj.permissions.all():
            codenames.append(permission.codename)
        codenames.sort()
        return format_html("<BR>".join(codenames))
