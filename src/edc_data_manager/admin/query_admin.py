from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.admin.options import StackedInline
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.inlines import StackedInlineMixin

from ..admin_site import edc_data_manager_admin
from ..forms import QueryForm
from ..models import DataManagerQuery, Query
from django.urls.base import reverse
from django.utils.safestring import mark_safe


@register(Query, site=edc_data_manager_admin)
class QueryAdmin(admin.ModelAdmin):

    form = QueryForm

    autocomplete_fields = ["data_dictionary", "visit_schedule"]

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "comment",
                    "status",
                    "data_manager_query",
                    "title",
                    "data_dictionary",
                    "visit_schedule",
                    "query",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = ("title", "status", "dm_query")

    list_filter = ("status",)

    def dm_query(self, obj):
        if obj:
            url_name = "_".join(obj.data_manager_query._meta.label_lower.split("."))
            namespace = edc_data_manager_admin.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return mark_safe(
                f'<a title="go to {obj._meta.verbose_name}" '
                f'href="{url}?q={obj.data_manager_query.action_identifier}">'
                f"{obj.data_manager_query.identifier}</a>"
            )
        return "DM Query"

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        readonly_fields = [
            "data_manager_query",
            "title",
            "data_dictionary",
            "visit_schedule",
            "query",
        ]
        return list(fields) + readonly_fields


class QueryAdminInline(StackedInlineMixin, StackedInline):
    model = Query
    form = QueryForm
    extra = 0
    autocomplete_fields = ["data_dictionary", "visit_schedule"]

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "title",
                    "data_dictionary",
                    "visit_schedule",
                    "query",
                    "status",
                )
            },
        ],
        audit_fieldset_tuple,
    )
