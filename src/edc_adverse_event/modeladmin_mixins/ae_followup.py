from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ActionItemModelAdminMixin
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..forms import AeFollowupForm
from ..templatetags.edc_adverse_event_extras import (
    format_ae_followup_description,
    select_description_template,
)
from .modeladmin_mixins import AdverseEventModelAdminMixin, NonAeInitialModelAdminMixin


class AeFollowupModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    AdverseEventModelAdminMixin,
    ActionItemModelAdminMixin,
):
    form = AeFollowupForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "outcome_date",
                    "outcome",
                    "ae_grade",
                    "relevant_history",
                    "followup",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "outcome": admin.VERTICAL,
        "followup": admin.VERTICAL,
        "ae_grade": admin.VERTICAL,
    }

    def get_search_fields(self, request) -> tuple[str]:
        search_fields = super().get_search_fields(request)
        return tuple(
            set(
                search_fields
                + (
                    "action_identifier",
                    "ae_initial__subject_identifier",
                    "ae_initial__action_identifier",
                )
            )
        )

    def get_list_display(self, request) -> tuple[str]:
        list_display = super().get_list_display(request)
        custom_fields = (
            "identifier",
            "dashboard",
            "description",
            "initial_ae",
            "follow_up_reports",
            "user",
        )
        return custom_fields + tuple(f for f in list_display if f not in custom_fields)

    def get_list_filter(self, request) -> tuple[str]:
        list_filter = super().get_list_filter(request)
        custom_fields = ("ae_grade", "followup", "outcome_date", "outcome", "report_datetime")
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def description(self, obj):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        context = format_ae_followup_description({}, obj, 80)
        return render_to_string(select_description_template("aefollowup"), context)

    def status(self, obj):
        follow_up_reports = None
        if obj.followup == YES:
            try:
                ae_followup = self.model.objects.get(parent_action_item=obj.action_item)
            except ObjectDoesNotExist:
                pass
            else:
                follow_up_reports = self.follow_up_reports(ae_followup)
        elif obj.followup == NO and obj.ae_grade != NOT_APPLICABLE:
            follow_up_reports = self.initial_ae(obj)
        if follow_up_reports:
            return format_html(  # nosec B703, B308
                "{}. See {}",
                mark_safe(obj.get_outcome_display()),  # nosec B703, B308
                mark_safe(follow_up_reports),  # nosec B703, B308
            )
        return obj.get_outcome_display()

    def follow_up_reports(self, obj):
        return super().follow_up_reports(obj.ae_initial)

    def initial_ae(self, obj):
        """Returns a shortened action identifier."""
        if obj.ae_initial:
            url_name = "_".join(obj.ae_initial._meta.label_lower.split("."))
            namespace = self.admin_site.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return format_html(  # nosec B703, B308
                '<a data-toggle="tooltip" title="go to ae initial report" '
                'href="{}?q={}">'
                "{}</a>",
                mark_safe(url),  # nosec B703, B308
                obj.ae_initial.action_identifier,
                obj.ae_initial.identifier,
            )
        return None
