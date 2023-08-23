from typing import Optional, Tuple

from django.apps import apps as django_apps
from django.contrib import admin
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin as BaseSimpleHistoryAdmin

format_html_lazy = lazy(format_html, str)


class SimpleHistoryAdmin(BaseSimpleHistoryAdmin):
    history_list_display: Tuple[str, ...] = ("dashboard", "change_message")
    object_history_template = "edc_model_admin/admin/object_history.html"
    object_history_form_template = "edc_model_admin/admin/object_history_form.html"

    save_as = False
    save_as_continue = False

    @admin.display(description=_("Change Message"))
    def change_message(self, obj) -> Optional[str]:
        log_entry_model_cls = django_apps.get_model("admin.logentry")
        log_entry = (
            log_entry_model_cls.objects.filter(
                action_time__gte=obj.modified, object_id=str(obj.id)
            )
            .order_by("action_time")
            .first()
        )
        if log_entry:
            return format_html(log_entry.get_change_message())
        return None

    def dashboard(self, obj) -> Optional[str]:
        if callable(self.view_on_site):
            return format_html_lazy(
                _('<A href="%(url)s">Dashboard</A>') % {"url": self.view_on_site(obj)}
            )
        return None

    def get_list_display(self, request) -> Tuple[str, ...]:
        return tuple(super().get_list_display(request))

    def get_list_filter(self, request) -> Tuple[str, ...]:
        return tuple(super().get_list_filter(request))

    def get_search_fields(self, request) -> Tuple[str, ...]:
        return tuple(super().get_search_fields(request))

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        return tuple(super().get_readonly_fields(request, obj=obj))

    def history_view_title(self, request, obj):
        word = _("View") if self.revert_disabled else _("Revert")
        return _("%(word)s %(verbose_name)s Audit Trail") % dict(
            word=str(word), verbose_name=obj._meta.verbose_name.title()
        )

    def history_form_view_title(self, request, obj):
        return self.history_view_title(request, obj)
