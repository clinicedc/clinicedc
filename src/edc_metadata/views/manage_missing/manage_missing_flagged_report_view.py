from __future__ import annotations

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ...models import (
    CrfMetadataMissing,
    DataMissingReason,
    RequisitionMetadataMissing,
)
from ...view_mixins import AllowedSitesViewMixin


def _verbose(label: str) -> str:
    try:
        return str(django_apps.get_model(label)._meta.verbose_name)
    except LookupError:
        return label


class ManageMissingFlaggedReportView(
    PermissionRequiredMixin,
    AllowedSitesViewMixin,
    EdcViewMixin,
    NavbarViewMixin,
    TemplateView,
):
    """A flat, DataTable-driven report of every CRF/requisition flagged as
    'data unavailable', filterable by reason. Site-scoped."""

    template_name = "edc_metadata/manage_missing_flagged.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "data_manager_home"
    permission_required = "edc_metadata.view_crfmetadatamissing"

    def get_context_data(self, **kwargs) -> dict:
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            rows=self.gather_rows(self.allowed_site_ids()),
            reason_choices=DataMissingReason.objects.all().order_by("display_index"),
        )
        return kwargs

    @classmethod
    def gather_rows(cls, allowed: list[int]) -> list[dict]:
        rows = [
            cls._row(obj, _verbose(obj.model), cls.get_url(obj))
            for obj in CrfMetadataMissing.objects.filter(site_id__in=allowed).select_related(
                "reason"
            )
        ]
        rows += [
            cls._row(obj, f"{_verbose(obj.model)} ({obj.panel_name})", cls.get_url(obj))
            for obj in RequisitionMetadataMissing.objects.filter(
                site_id__in=allowed
            ).select_related("reason")
        ]
        rows.sort(key=lambda r: r["modified"], reverse=True)
        return rows

    @staticmethod
    def get_url(obj: CrfMetadataMissing) -> str:
        return reverse(
            "edc_metadata:manage_missing_by_subject_url",
            kwargs=dict(
                subject_identifier=obj.subject_identifier,
                visit_schedule_name=obj.visit_schedule_name,
                schedule_name=obj.schedule_name,
                visit_code=obj.visit_code,
            ),
        )

    @staticmethod
    def _row(obj, form: str, url: str) -> dict:
        return dict(
            subject_identifier=obj.subject_identifier,
            form=form,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
            reason=obj.reason.display_name,
            comment=obj.comment,
            modified=obj.modified,
            user=obj.user_modified,
            url=url,
        )
