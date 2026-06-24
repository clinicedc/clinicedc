from __future__ import annotations

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

from ..constants import REQUIRED
from ..models import (
    CrfMetadata,
    CrfMetadataUnavailable,
    DataUnavailableReason,
    RequisitionMetadata,
    RequisitionMetadataUnavailable,
)
from ..view_mixins import SiteScopeViewMixin

# kind -> (source metadata cls, unavailable cls, unavailable model_name)
KINDS = {
    "crf": (CrfMetadata, CrfMetadataUnavailable, "crfmetadataunavailable"),
    "requisition": (
        RequisitionMetadata,
        RequisitionMetadataUnavailable,
        "requisitionmetadataunavailable",
    ),
}


class ReviewOutstandingDetailView(
    PermissionRequiredMixin,
    SiteScopeViewMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """Per (subject, visit) list of outstanding CRFs/requisitions with a
    'mark unavailable' / un-flag action. The review board drills into this
    page and it is the subject dashboard's review entry point."""

    template_name = "edc_metadata/review_outstanding_flag_unflag.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_metadata.view_crfmetadata"

    def can_flag(self, model_name: str) -> bool:
        return self.request.user.has_perms(
            [f"edc_metadata.add_{model_name}", f"edc_metadata.delete_{model_name}"]
        )

    def natural_key_opts(self) -> dict:
        return dict(
            subject_identifier=self.kwargs["subject_identifier"],
            visit_schedule_name=self.kwargs["visit_schedule_name"],
            schedule_name=self.kwargs["schedule_name"],
            visit_code=self.kwargs["visit_code"],
        )

    # --------------------------------------------------------------------- GET
    def get_context_data(self, **kwargs) -> dict:
        kwargs = super().get_context_data(**kwargs)
        opts = self.natural_key_opts()
        allowed = self.allowed_site_ids()

        kwargs.update(
            **opts,
            crf_rows=self._rows(
                CrfMetadata, CrfMetadataUnavailable, "crf", opts, allowed, panel=False
            ),
            req_rows=self._rows(
                RequisitionMetadata,
                RequisitionMetadataUnavailable,
                "requisition",
                opts,
                allowed,
                panel=True,
            ),
            reason_choices=DataUnavailableReason.objects.all().order_by("display_index"),
            can_flag_crf=self.can_flag("crfmetadataunavailable"),
            can_flag_req=self.can_flag("requisitionmetadataunavailable"),
            dashboard_url=self._dashboard_url(opts, allowed),
            back_url=self._back_url(opts),
            review_flagged_url=self.review_flagged_url(opts),
            now=timezone.now(),
        )
        return kwargs

    @staticmethod
    def _rows(source_cls, unavailable_cls, kind, opts, allowed, panel: bool) -> list[dict]:
        meta_qs = source_cls.objects.filter(
            entry_status=REQUIRED, site_id__in=allowed, **opts
        ).order_by("visit_code_sequence", "show_order")
        flags = {}
        for f in unavailable_cls.objects.filter(**opts):
            key = (
                (f.model, f.panel_name, f.visit_code_sequence)
                if panel
                else (f.model, f.visit_code_sequence)
            )
            flags[key] = f
        rows = []
        for m in meta_qs:
            key = (
                (m.model, m.panel_name, m.visit_code_sequence)
                if panel
                else (m.model, m.visit_code_sequence)
            )
            rows.append(dict(meta=m, kind=kind, flag=flags.get(key)))
        return rows

    def _dashboard_url(self, opts, allowed) -> str | None:
        appointment_cls = django_apps.get_model("edc_appointment.appointment")
        appt = appointment_cls.objects.filter(
            site_id__in=allowed, visit_code_sequence=0, **opts
        ).first()
        if not appt:
            return None
        return reverse(
            url_names.get("subject_dashboard_url"),
            kwargs=dict(
                subject_identifier=opts["subject_identifier"], appointment=str(appt.id)
            ),
        )

    @staticmethod
    def _back_url(opts) -> str:
        query = urlencode(
            [
                ("lens", "grid"),
                ("submitted", "1"),
                ("schedule", f"{opts['visit_schedule_name']}::{opts['schedule_name']}"),
                ("visit_code", opts["visit_code"]),
            ]
        )
        return f"{reverse('edc_metadata:review_grid_url')}?{query}"

    @staticmethod
    def review_flagged_url(opts) -> str:
        query = urlencode(
            [
                ("search", f"{opts['subject_identifier']}"),
            ]
        )
        return f"{reverse('edc_metadata:unavailable_report_url')}?{query}"

    # -------------------------------------------------------------------- POST
    def post(self, request, *args, **kwargs):  # noqa: ARG002
        """Reconcile every row in the submitted panel against its reason: a
        reason creates/updates the flag, a blank reason removes it."""
        redirect = HttpResponseRedirect(
            reverse("edc_metadata:metadata_detail_url", kwargs=self.kwargs)
        )
        kind = request.POST.get("kind")
        if kind not in KINDS:
            messages.error(request, "Invalid request.")
            return redirect

        source_cls, unavailable_cls, model_name = KINDS[kind]
        if not self.can_flag(model_name):
            raise PermissionDenied

        allowed = self.allowed_site_ids()
        is_req = kind == "requisition"
        flagged = cleared = skipped = 0
        for i in request.POST.getlist("rows"):
            natkey = dict(
                **self.natural_key_opts(),
                visit_code_sequence=request.POST.get(f"seq_{i}") or 0,
                model=request.POST.get(f"model_{i}"),
            )
            if is_req:
                natkey["panel_name"] = request.POST.get(f"panel_{i}", "")
            # site-scope guard: the source metadata must belong to an allowed site
            source = source_cls.objects.filter(**natkey).first()
            if not source or source.site_id not in allowed:
                skipped += 1
                continue
            reason_id = request.POST.get(f"reason_{i}")
            if reason_id:
                username = request.user.username
                common = dict(
                    reason_id=reason_id,
                    comment=request.POST.get(f"comment_{i}") or "",
                    decision_datetime=timezone.now(),
                    site_id=source.site_id,
                )
                # django_audit_fields only fills user_* via the admin; this POST
                # path bypasses the admin, so set them here.
                unavailable_cls.objects.update_or_create(
                    **natkey,
                    defaults={**common, "user_modified": username},
                    create_defaults={
                        **common,
                        "user_created": username,
                        "user_modified": username,
                    },
                )
                flagged += 1
            else:
                deleted, _ = unavailable_cls.objects.filter(**natkey).delete()
                cleared += 1 if deleted else 0

        parts = []
        if flagged:
            parts.append(f"{flagged} flagged")
        if cleared:
            parts.append(f"{cleared} cleared")
        if skipped:
            parts.append(f"{skipped} skipped")
        messages.success(request, "Updated: " + (", ".join(parts) if parts else "no changes"))
        return redirect
