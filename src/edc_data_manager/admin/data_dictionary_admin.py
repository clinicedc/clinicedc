from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.admin import sites
from django.contrib.admin.decorators import register
from django.contrib.auth import get_permission_codename
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple, ModelAdminAuditFieldsMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_model_admin import SimpleHistoryAdmin

from ..admin_site import edc_data_manager_admin
from ..models import DataDictionary
from ..populate_data_dictionary import populate_data_dictionary


@register(DataDictionary, site=edc_data_manager_admin)
class DataDictionaryAdmin(ModelAdminAuditFieldsMixin, SimpleHistoryAdmin):

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "model",
                    "number",
                    "prompt",
                    "field_name",
                    "field_type",
                    "active",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    ordering = ("active", "model", "number")

    list_filter = ("active", "model", "field_type")

    list_display = (
        "form_title",
        "field_name",
        "active",
        "number",
        "question_text",
        "field_type",
    )

    actions = ["populate_data_dictionary_action"]

    search_fields = ("number", "prompt", "field_name", "model")

    def form_title(self, obj):
        try:
            model_cls = django_apps.get_model(obj.model)
        except (LookupError, ValueError):
            return str(obj.model)
        return model_cls._meta.verbose_name

    def question_text(self, obj):
        return mark_safe(obj.prompt)

    def populate_data_dictionary_action(self, request, queryset):
        DataDictionary.objects.update(active=False)
        for site in sites.all_sites.data:
            for model_admin in site()._registry.values():
                form = model_admin.get_form(request)
                model = model_admin.model
                if model._meta.app_label in settings.DATA_DICTIONARY_APP_LABELS and not issubclass(
                    model, (ListModelMixin,)
                ):
                    populate_data_dictionary(form=form, model=model)

    populate_data_dictionary_action.allowed_permissions = ("refresh",)
    populate_data_dictionary_action.short_description = "Refresh data dictionary"

    def has_refresh_permission(self, request):
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
