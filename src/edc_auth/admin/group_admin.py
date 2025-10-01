from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from edc_auth.admin_site import edc_auth_admin
from edc_model_admin.mixins import TemplatesModelAdminMixin

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
        codenames = [permission.codename for permission in obj.permissions.all()]
        codenames.sort()
        return mark_safe("<BR>".join(codenames))  # noqa: S308
