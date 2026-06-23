from __future__ import annotations

from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple

from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_metadata_admin
from ..models import CrfPriority
from .list_filters import (
    ScheduleNameListFilter,
    VisitScheduleNameListFilter,
    _iter_all_visits,
)


def valid_model_labels() -> set[str]:
    """Return the dotted labels of every CRF/requisition declared in the
    visit schedule registry."""
    labels: set[str] = set()
    for _vs, _sched, visit in _iter_all_visits():
        for attr in (
            "crfs",
            "crfs_prn",
            "crfs_unscheduled",
            "crfs_missed",
            "requisitions",
            "requisitions_prn",
            "requisitions_unscheduled",
        ):
            for form in getattr(visit, attr, []) or []:
                labels.add(form.model)
    return labels


class CrfPriorityForm(forms.ModelForm):
    def clean_model(self) -> str:
        model = self.cleaned_data["model"]
        labels = valid_model_labels()
        # only validate when the registry is loaded and populated
        if labels and model not in labels:
            raise forms.ValidationError(
                _("Invalid model label. Expected a CRF/requisition declared in a schedule.")
            )
        return model

    class Meta:
        model = CrfPriority
        fields = (
            "model",
            "visit_schedule_name",
            "schedule_name",
            "metadata_kind",
            "tier",
            "active",
        )


@admin.register(CrfPriority, site=edc_metadata_admin)
class CrfPriorityAdmin(TemplatesModelAdminMixin, ModelAdminAuditFieldsMixin, admin.ModelAdmin):
    show_object_tools = True
    form = CrfPriorityForm
    ordering = ("tier", "schedule_name", "model")
    list_display = (
        "model",
        "metadata_kind",
        "visit_schedule_name",
        "schedule_name",
        "tier",
        "active",
    )
    list_filter = (
        "active",
        "tier",
        "metadata_kind",
        ScheduleNameListFilter,
        VisitScheduleNameListFilter,
    )
    search_fields = ("model",)

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "model",
                    "visit_schedule_name",
                    "schedule_name",
                    "metadata_kind",
                    "tier",
                    "active",
                )
            },
        ],
        audit_fieldset_tuple,
    )
