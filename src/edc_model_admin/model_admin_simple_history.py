from django.apps import apps as django_apps
from django.utils.safestring import mark_safe
from simple_history.admin import SimpleHistoryAdmin as BaseSimpleHistoryAdmin


class SimpleHistoryAdmin(BaseSimpleHistoryAdmin):

    history_list_display = ["dashboard", "change_message"]

    save_as = False
    save_as_continue = False

    def change_message(self, obj):
        log_entry_model_cls = django_apps.get_model("admin.logentry")
        log_entry = (
            log_entry_model_cls.objects.filter(
                action_time__gte=obj.modified, object_id=str(obj.id)
            )
            .order_by("action_time")
            .first()
        )
        if log_entry:
            return mark_safe(log_entry.get_change_message())
        return None

    change_message.short_description = "Change Message"

    def dashboard(self, obj):
        if callable(self.view_on_site):
            return mark_safe(f'<A href="{self.view_on_site(obj)}">Dashboard</A>')
        return None
