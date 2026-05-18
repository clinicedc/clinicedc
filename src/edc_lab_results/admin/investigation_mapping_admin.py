from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    TemplatesModelAdminMixin,
)
from edc_notification.modeladmin_mixins import (
    NotificationModelAdminMixin,
)

from ..admin_site import edc_lab_results_admin
from ..models import InvestigationMapping


@admin.register(
    InvestigationMapping, site=edc_lab_results_admin
)
class InvestigationMappingAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    ModelAdminAuditFieldsMixin,
    admin.ModelAdmin,
):
    list_display = (
        "investigation",
        "link_to_reportable",
        "laboratory",
        "in_reportable",
        "modified",
    )
    list_filter = ("laboratory", "in_reportable", "utest_id")
    search_fields = ("investigation", "utest_id", "laboratory")
    ordering = ("laboratory", "investigation")

    @admin.display(description="UTESTID", ordering="utest_id")
    def link_to_reportable(self, obj):
        if obj.utest_id:
            url = reverse(
                "edc_reportable_admin:"
                "edc_reportable_normaldata_changelist"
            )
            return format_html(
                '<A href="{url}?q={utestid}">{utestid}</A>',
                url=url,
                utestid=obj.utest_id,
            )
        return None
