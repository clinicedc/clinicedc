from django.conf import settings
from django.contrib import admin
from django.contrib.admin import sites
from django.contrib.auth import get_permission_codename
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import ModelAdminAuditFieldsMixin, audit_fieldset_tuple
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_list_data.model_mixins import ListModelMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.mixins import (
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    TemplatesModelAdminMixin,
)
from edc_notification.modeladmin_mixins import NotificationModelAdminMixin

from ..admin_site import edc_data_manager_admin
from ..forms import DataDictionaryForm
from ..models import DataDictionary
from ..populate_data_dictionary import populate_data_dictionary


@admin.register(DataDictionary, site=edc_data_manager_admin)
class DataDictionaryAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    ModelAdminAuditFieldsMixin,
    SimpleHistoryAdmin,
):

    form = DataDictionaryForm

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "model",
                    "model_verbose_name",
                    "number",
                    "prompt",
                    "field_name",
                    "field_type",
                    "help_text",
                    "default_value",
                    "nullable",
                    "max_length",
                    "max_digits",
                    "decimal_places",
                    "active",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    ordering = ("active", "model", "number")

    list_filter = ("active", "model", "field_type", "nullable")

    list_display = (
        "form_title",
        "field_name",
        "changelist_link",
        "active",
        "number",
        "question_text",
        "field_type",
        "default_value",
        "help_text",
        "nullable",
        "max_length",
        "max_digits",
        "decimal_places",
    )

    actions = ("populate_data_dictionary_action",)

    search_fields = (
        "number",
        "prompt",
        "field_name",
        "model",
        "help_text",
        "model_verbose_name",
    )

    readonly_fields = [
        "model",
        "model_verbose_name",
        "number",
        "prompt",
        "field_name",
        "field_type",
        "help_text",
        "default_value",
        "nullable",
        "max_length",
        "max_digits",
        "decimal_places",
        "active",
    ]

    @admin.display(description="Changelist")
    def changelist_link(self, obj):
        for site in sites.all_sites.data:
            for modeladmin in site()._registry.values():
                if modeladmin.model._meta.label_lower == obj.model:
                    model_string = obj.model.replace(".", "_")
                    try:
                        url = reverse(f"{site().name}:{model_string}_changelist")
                    except NoReverseMatch:
                        pass
                    else:
                        return format_html(
                            '<a href="{url}">Changelist</a>',
                            url=mark_safe(url),  # nosec B703 B308
                        )
        return None

    @staticmethod
    def form_title(obj):
        return obj.model_verbose_name

    @staticmethod
    def question_text(obj):
        return format_html(
            "{}",
            mark_safe(obj.prompt),  # nosec B703, B308
        )

    def populate_data_dictionary_action(self, request, queryset):
        DataDictionary.objects.update(active=False)
        for site in sites.all_sites.data:
            for model_admin in site()._registry.values():
                form = model_admin.get_form(request)
                model = model_admin.model
                if (
                    model._meta.app_label in settings.DATA_DICTIONARY_APP_LABELS
                    and not issubclass(model, (ListModelMixin,))
                ):
                    populate_data_dictionary(form=form, model=model)

    populate_data_dictionary_action.allowed_permissions = ("refresh",)
    populate_data_dictionary_action.short_description = "Refresh data dictionary"

    def has_refresh_permission(self, request):
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
