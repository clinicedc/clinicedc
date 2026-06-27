from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView

from edc_dashboard.url_names import url_names
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ...constants import CRF, REQUIRED, REQUISITION
from ...models import (
    CrfMetadata,
    CrfMetadataMissing,
    DataMissingReason,
    RequisitionMetadata,
    RequisitionMetadataMissing,
)
from ...view_mixins import AllowedSitesViewMixin
from .manage_missing_view import visit_type_filter

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

METADATA_TYPES = {
    CRF: (CrfMetadata, CrfMetadataMissing, "crfmetadatamissing"),
    REQUISITION: (
        RequisitionMetadata,
        RequisitionMetadataMissing,
        "requisitionmetadatamissing",
    ),
}


class ManageMissingFlagUnFlagView(
    PermissionRequiredMixin,
    AllowedSitesViewMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """Per (subject, visit) list of missing CRFs/requisitions with
    a flag / un-flag action. The view by subject table drills into
    this page.

    See also: ManageMissingView.
    """

    template_name = "edc_metadata/manage_missing_flag_unflag.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_metadata.view_crfmetadata"

    def has_perms_for(self, model_name: str) -> bool:
        return self.request.user.has_perms(
            [f"edc_metadata.add_{model_name}", f"edc_metadata.delete_{model_name}"]
        )

    def default_filter_opts(self) -> dict:
        return dict(
            subject_identifier=self.kwargs.get("subject_identifier"),
            visit_schedule_name=self.kwargs.get("visit_schedule_name"),
            schedule_name=self.kwargs.get("schedule_name"),
            visit_code=self.kwargs.get("visit_code"),
        )

    def selected_visit_type(self) -> str:
        """"scheduled"/"unscheduled" carried from the manage-missing grid,
        or "" (all)."""
        value = self.request.GET.get("visit_type")
        return value if value in ("scheduled", "unscheduled") else ""

    def get_context_data(self, **kwargs) -> dict:
        kwargs = super().get_context_data(**kwargs)
        opts = {k: v for k, v in self.default_filter_opts().items() if v}
        visit_type = self.selected_visit_type()
        # narrow the listed rows to scheduled/unscheduled when carried from the
        # grid; keep `opts` clean for the url builders (dashboard_url pins
        # visit_code_sequence=0 itself).
        row_opts = {**opts, **visit_type_filter(visit_type)}
        allowed_site_ids = self.allowed_site_ids()
        kwargs.update(
            **opts,
            selected_visit_type=visit_type,
            crf_rows=self.get_crf_rows(row_opts, allowed_site_ids),
            requisition_rows=self.get_requisition_rows(row_opts, allowed_site_ids),
            reason_choices=DataMissingReason.objects.all().order_by("display_index"),
            can_flag_crf=self.has_perms_for("crfmetadatamissing"),
            can_flag_requisition=self.has_perms_for("requisitionmetadatamissing"),
            dashboard_url=self.dashboard_url(opts, allowed_site_ids),
            dashboard_url_name=url_names.get("subject_dashboard_url"),
            back_url=self.back_url(opts, visit_type),
            review_flagged_url=self.review_flagged_url(opts),
            now=timezone.now(),
            CRF=CRF,
            REQUISITION=REQUISITION,
            REQUIRED=REQUIRED,
        )
        return kwargs

    def get_crf_rows(self, opts, allowed):
        return self._get_rows(CrfMetadata, CrfMetadataMissing, CRF, opts, allowed, panel=False)

    def get_requisition_rows(self, opts, allowed):
        return self._get_rows(
            RequisitionMetadata,
            RequisitionMetadataMissing,
            REQUISITION,
            opts,
            allowed,
            panel=True,
        )

    @staticmethod
    def get_appointment(**opts) -> Appointment | None:
        appointment_cls = django_apps.get_model("edc_appointment.appointment")
        if obj := appointment_cls.objects.filter(**opts).first():
            return obj
        return None

    def dashboard_url(self, opts, allowed) -> str | None:
        if appt := self.get_appointment(site_id__in=allowed, visit_code_sequence=0, **opts):
            return reverse(
                url_names.get("subject_dashboard_url"),
                kwargs=dict(
                    subject_identifier=opts["subject_identifier"], appointment=str(appt.id)
                ),
            )
        return None

    @staticmethod
    def back_url(opts, visit_type=None) -> str:
        params = [
            ("lens", "grid"),
            ("submitted", "1"),
            ("schedule", f"{opts['visit_schedule_name']}::{opts['schedule_name']}"),
            ("subject_identifier", opts["subject_identifier"]),
            ("visit_code", opts["visit_code"]),
        ]
        if visit_type:
            params.append(("visit_type", visit_type))
        query = urlencode(params)
        return f"{reverse('edc_metadata:manage_missing_url')}?{query}"

    @staticmethod
    def review_flagged_url(opts) -> str:
        query = urlencode(
            [
                ("search", f"{opts['subject_identifier']}"),
                ("subject_identifier", f"{opts['subject_identifier']}"),
            ]
        )
        return f"{reverse('edc_metadata:manage_missing_flagged_url')}?{query}"

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        """Reconcile every row in the submitted panel against its reason: a
        reason creates/updates the flag, a blank reason removes it."""
        # keep the scheduled/unscheduled selection on the post-submit reload
        visit_type = self.selected_visit_type()
        redirect_url = reverse(
            "edc_metadata:manage_missing_by_subject_url", kwargs=self.kwargs
        )
        if visit_type:
            redirect_url += f"?{urlencode({'visit_type': visit_type})}"
        redirect = HttpResponseRedirect(redirect_url)
        metadata_category = request.POST.get("metadata_category")
        if metadata_category not in METADATA_TYPES:
            messages.error(request, f"Unknown metadata category. Got {metadata_category}.")
            return redirect

        metadata_model_cls, metadata_missing_model_cls, model_name = METADATA_TYPES[
            metadata_category
        ]
        if not self.has_perms_for(model_name):
            raise PermissionDenied

        allowed = self.allowed_site_ids()
        flagged = cleared = skipped = 0
        for i in request.POST.getlist("rows"):
            filter_opts = dict(
                **self.default_filter_opts(),
                visit_code_sequence=request.POST.get(f"seq_{i}") or 0,
                model=request.POST.get(f"model_{i}"),
            )
            if metadata_category == REQUISITION:
                filter_opts["panel_name"] = request.POST.get(f"panel_{i}", "")
            metadata_obj = metadata_model_cls.objects.filter(**filter_opts).first()
            if not metadata_obj or metadata_obj.site_id not in allowed:
                skipped += 1
                continue
            if reason_id := request.POST.get(f"reason_{i}"):
                username = request.user.username
                default_opts = dict(
                    reason_id=reason_id,
                    comment=request.POST.get(f"comment_{i}") or "",
                    decision_datetime=timezone.now(),
                    site_id=metadata_obj.site_id,
                )
                metadata_missing_model_cls.objects.update_or_create(
                    **filter_opts,
                    defaults={**default_opts, "user_modified": username},
                    create_defaults={
                        **default_opts,
                        "user_created": username,
                        "user_modified": username,
                    },
                )
                flagged += 1
            else:
                deleted, _ = metadata_missing_model_cls.objects.filter(**filter_opts).delete()
                cleared += 1 if deleted else 0

        parts = []
        if flagged:
            parts.append(f"{flagged} flagged")
        if cleared:
            parts.append(f"{cleared} cleared")
        if skipped:
            parts.append(f"{skipped} skipped")
        metadata_category = (
            metadata_category.upper()
            if metadata_category == CRF
            else metadata_category.title()
        )
        messages.success(
            request,
            f"Updated {metadata_category}s: " + (", ".join(parts) if parts else "no changes"),
        )
        return redirect

    def _get_rows(
        self,
        metadata_model_cls: type[CrfMetadata | RequisitionMetadata],
        metadata_missing_model_cls: type[CrfMetadataMissing | RequisitionMetadataMissing],
        metadata_category: str,
        opts: dict,
        allowed,
        panel: bool,
    ) -> list[dict]:

        flags = {}
        for obj in metadata_missing_model_cls.objects.filter(**opts):
            key = (
                (obj.model, obj.panel_name, obj.visit_code_sequence)
                if panel
                else (obj.model, obj.visit_code_sequence)
            )
            flags[key] = obj

        rows = []
        metadata_qs = metadata_model_cls.objects.filter(
            entry_status=REQUIRED, site_id__in=allowed, **opts
        ).order_by("visit_code_sequence", "show_order")
        for obj in metadata_qs:
            key = (
                (obj.model, obj.panel_name, obj.visit_code_sequence)
                if panel
                else (obj.model, obj.visit_code_sequence)
            )
            obj.appointment = self.get_appointment(
                subject_identifier=obj.subject_identifier,
                visit_code=obj.visit_code,
                visit_code_sequence=obj.visit_code_sequence,
                visit_schedule_name=obj.visit_schedule_name,
                schedule_name=obj.schedule_name,
            )
            rows.append(
                dict(meta=obj, metadata_category=metadata_category, flag=flags.get(key))
            )
        return rows
