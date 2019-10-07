from django import forms
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ModelAdminActionItemMixin
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..get_ae_model import get_ae_model
from ..modelform_mixins import AeSusarModelFormMixin
from ..templatetags.edc_adverse_event_extras import (
    format_ae_susar_description,
    format_ae_susar_description_template_name,
)
from .modeladmin_mixins import NonAeInitialModelAdminMixin


class AeSusarForm(AeSusarModelFormMixin, forms.ModelForm):
    class Meta:
        model = get_ae_model("aesusar")
        fields = "__all__"


# @admin.register(AeSusar, site=ambition_ae_admin)
class AeSusarModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    ModelAdminActionItemMixin,
):

    form = AeSusarForm

    list_display = [
        "subject_identifier",
        "dashboard",
        "description",
        "initial_ae",
        "report_datetime",
    ]

    list_filter = ("report_datetime", "submitted_datetime")

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
        "ae_initial__tracking_identifier",
        "tracking_identifier",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "submitted_datetime",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {"report_status": admin.VERTICAL}

    def description(self, obj):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        context = format_ae_susar_description({}, obj, 50)
        return render_to_string(format_ae_susar_description_template_name, context)

    def initial_ae(self, obj):
        """Returns a shortened action identifier.
        """
        if obj.ae_initial:
            url_name = "_".join(obj.ae_initial._meta.label_lower.split("."))
            namespace = self.admin_site.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return mark_safe(
                f'<a data-toggle="tooltip" title="go to ae initial report" '
                f'href="{url}?q={obj.ae_initial.action_identifier}">'
                f"{obj.ae_initial.identifier}</a>"
            )
        return None
