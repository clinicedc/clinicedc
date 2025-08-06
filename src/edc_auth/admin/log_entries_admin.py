from django.contrib import admin
from django.contrib.admin.models import LogEntry
from logentry_admin.admin import ActionListFilter, LogEntryAdmin, UserListFilter

from edc_auth.admin_site import edc_auth_admin
from edc_model_admin.mixins import TemplatesModelAdminMixin

admin.site.unregister(LogEntry)


@admin.register(LogEntry, site=edc_auth_admin)
class LogEntriesAdmin(TemplatesModelAdminMixin, LogEntryAdmin):
    list_filter = (
        "action_time",
        ActionListFilter,
        UserListFilter,
        "content_type",
    )
