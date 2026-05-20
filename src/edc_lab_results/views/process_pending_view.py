from __future__ import annotations

import shutil
from pathlib import Path
from zoneinfo import ZoneInfo

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..constants import PENDING
from ..import_results import (
    LabResultImporter,
    LabResultImportError,
    best_guess_utest_id,
)
from ..models import UploadedResultFile


def _get_laboratory_choices() -> list[tuple[str, str]]:
    parsers: dict = getattr(settings, "EDC_LAB_PARSERS", {})
    return [(k, k) for k in sorted(parsers.keys())]


def _get_default_laboratory() -> str:
    return getattr(settings, "EDC_LAB_RESULTS_DEFAULT_LABORATORY", "")


def _pending_file_paths() -> list[Path]:
    base = Path(settings.EDC_LAB_RESULTS_UPLOAD_DIR).expanduser()
    pending_dir = base / "pending"
    pending_qs = UploadedResultFile.objects.filter(status=PENDING)
    paths = []
    for upload in pending_qs:
        p = pending_dir / upload.stored_filename
        if p.exists():
            paths.append(p)
    return paths


class ProcessPendingView(EdcViewMixin, NavbarViewMixin, TemplateView):
    """Two-step processing of pending uploads.

    GET with ``step=review`` in session → show the review page.
    POST without ``confirm`` → pre-scan pending files, redirect to review.
    POST with ``confirm`` → save mappings and run the full import.
    """

    template_name = "edc_lab_results/process_review.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        review = self.request.session.get("process_review", {})
        context.update(
            laboratory=review.get("laboratory", ""),
            file_count=review.get("file_count", 0),
            result_count=review.get("result_count", 0),
            mapped=review.get("mapped", []),
            unmapped=review.get("unmapped", []),
            laboratory_choices=_get_laboratory_choices(),
        )
        return context

    def get(self, request: object, *args: object, **kwargs: object) -> object:
        if not request.session.get("process_review"):
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))
        return super().get(request, *args, **kwargs)

    def post(self, request: object, *args: object, **kwargs: object) -> object:  # noqa: ARG002
        if "confirm" in request.POST:
            return self._handle_confirm(request)
        return self._handle_scan(request)

    def _handle_scan(self, request: object) -> HttpResponseRedirect:
        laboratory = request.POST.get("laboratory", "").strip()
        if not laboratory:
            messages.error(request, "Select a laboratory.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        pending_count = UploadedResultFile.objects.filter(status=PENDING).count()
        if not pending_count:
            messages.info(request, "No pending files to process.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        file_paths = _pending_file_paths()
        if not file_paths:
            messages.error(request, "Pending files not found on disk.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        importer = LabResultImporter(laboratory)
        tz = ZoneInfo(settings.TIME_ZONE)
        try:
            df = importer.parse_files(file_paths, tz=tz)
        except LabResultImportError as e:
            messages.error(request, f"Parse error: {e}")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        if df.empty:
            messages.warning(request, "No results extracted from pending files.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        # Identify mapped vs unmapped investigations
        InvestigationMapping = apps.get_model(
            "edc_lab_results", "InvestigationMapping"
        )
        NormalData = apps.get_model("edc_reportable", "NormalData")
        known_utest_ids = set(
            NormalData.objects.values_list("label", flat=True).distinct()
        )
        default_mappings: dict = getattr(
            settings, "EDC_LAB_DEFAULT_MAPPINGS", {}
        ).get(laboratory, {})

        investigations = sorted(df["investigation"].unique())
        existing = {
            m.investigation: m.utest_id
            for m in InvestigationMapping.objects.filter(
                laboratory=laboratory, investigation__in=investigations
            )
        }

        mapped = []
        unmapped = []
        for inv in investigations:
            if inv in existing:
                mapped.append({"investigation": inv, "utest_id": existing[inv]})
            else:
                guess = best_guess_utest_id(inv, known_utest_ids, default_mappings)
                unmapped.append({"investigation": inv, "guess": guess})

        request.session["process_review"] = {
            "laboratory": laboratory,
            "file_count": len(file_paths),
            "result_count": len(df),
            "mapped": mapped,
            "unmapped": unmapped,
        }

        return HttpResponseRedirect(reverse("edc_lab_results:process-pending"))

    def _handle_confirm(self, request: object) -> HttpResponseRedirect:
        review = request.session.pop("process_review", {})
        laboratory = review.get("laboratory", "")
        if not laboratory:
            messages.error(request, "Session expired. Please try again.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        # Save new investigation mappings from the form
        InvestigationMapping = apps.get_model(
            "edc_lab_results", "InvestigationMapping"
        )
        NormalData = apps.get_model("edc_reportable", "NormalData")

        for item in review.get("unmapped", []):
            inv = item["investigation"]
            utest_id = request.POST.get(f"utest_id_{inv}", "").strip()
            in_reportable = bool(
                utest_id and NormalData.objects.filter(label=utest_id).exists()
            )
            InvestigationMapping.objects.update_or_create(
                laboratory=laboratory,
                investigation=inv,
                defaults={
                    "utest_id": utest_id,
                    "in_reportable": in_reportable,
                },
            )

        # Re-parse and run full import
        importer = LabResultImporter(laboratory)
        tz = ZoneInfo(settings.TIME_ZONE)
        file_paths = _pending_file_paths()

        if not file_paths:
            messages.error(request, "No pending files found on disk.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        try:
            df = importer.parse_files(file_paths, tz=tz)
        except LabResultImportError as e:
            messages.error(request, f"Parse error: {e}")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        if df.empty:
            messages.warning(request, "No results extracted.")
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))

        mapping_summary = importer.resolve_mappings(df)
        save_summary = importer.save_results(df, mapping_summary.utest_map)
        link_summary = importer.link_requisitions()

        # Update UploadedResultFile statuses and move files
        base = Path(settings.EDC_LAB_RESULTS_UPLOAD_DIR).expanduser()
        pending_dir = base / "pending"
        processed_dir = base / "processed"
        now = timezone.now()

        for upload in UploadedResultFile.objects.filter(status=PENDING):
            source = pending_dir / upload.stored_filename
            if source.exists():
                shutil.move(str(source), str(processed_dir / upload.stored_filename))
            upload.status = "imported"
            upload.imported_datetime = now
            upload.save(update_fields=["status", "imported_datetime"])

        messages.success(
            request,
            f"Imported {save_summary.created} results from "
            f"{review.get('file_count', 0)} file(s). "
            f"Skipped {save_summary.skipped} duplicates. "
            f"Requisitions: {link_summary.linked} linked, "
            f"{link_summary.ambiguous} ambiguous, "
            f"{link_summary.no_match} no match.",
        )
        return HttpResponseRedirect(reverse("edc_lab_results:upload"))
