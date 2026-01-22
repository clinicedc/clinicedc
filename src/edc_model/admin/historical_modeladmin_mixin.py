from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from edc_utils import to_local


class HistoricalModelAdminMixin:
    change_list_note_url_name: str = ""

    @property
    def change_list_note(self):
        url = reverse(self.change_list_note_url_name)
        return format_html(
            "You are viewing the <B>transaction history</B> for this form. Click "
            '<A href="{}">here</A> to see the live data.',
            url,
        )

    @admin.display(description="History date", ordering="history_date")
    def formatted_history_date(self, obj):
        if obj.history_date:
            return to_local(obj.history_date)
        return None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
