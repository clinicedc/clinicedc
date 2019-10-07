from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item import action_fieldset_tuple
from edc_action_item.modeladmin_mixins import ModelAdminActionItemMixin
from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from .modeladmin_mixins import NonAeInitialModelAdminMixin


class AeFollowupModelAdminMixin(
    ModelAdminSubjectDashboardMixin,
    NonAeInitialModelAdminMixin,
    ModelAdminActionItemMixin,
):

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

    list_display = (
        "identifier",
        "dashboard",
        "subject_identifier",
        "outcome_date",
        "initial_ae",
        "description",
        "severity",
        "status",
        "follow_up_report",
        "user_created",
    )

    list_filter = ("ae_grade", "followup", "outcome_date", "report_datetime")

    search_fields = [
        "action_identifier",
        "ae_initial__tracking_identifier",
        "ae_initial__subject_identifier",
        "ae_initial__action_identifier",
    ]

    def description(self, obj):
        return obj.relevant_history

    def follow_up_report(self, obj):
        return obj.followup

    def status(self, obj):
        link = None
        if obj.followup == YES:
            try:
                ae_followup = self.model.objects.get(parent_action_item=obj.action_item)
            except ObjectDoesNotExist:
                ae_followup = None
            link = self.ae_followup(ae_followup)
        elif obj.followup == NO and obj.ae_grade != NOT_APPLICABLE:
            link = self.initial_ae(obj)
        if link:
            return mark_safe(f"{obj.get_outcome_display()}. See {link}.")
        return obj.get_outcome_display()

    def ae_followup(self, obj):
        if obj:
            url_name = "_".join(obj._meta.label_lower.split("."))
            namespace = self.admin_site.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            return mark_safe(
                f'<a title="go to next {obj._meta.verbose_name} report" '
                f'href="{url}?q={obj.action_identifier}">'
                f"{obj.identifier}</a>"
            )
        return "AE Followup"

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
