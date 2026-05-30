from __future__ import annotations

import logging
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from clinicedc_constants import CRF_ISSUE_DETECTED, NO, NOT_APPLICABLE
from django.apps import apps
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from ..models import Result as ResultModel
from .discovery import CrfInfo, build_utest_to_panel_map, discover_crf_models
from .summary import TranscribeDetail, TranscribeSummary

if TYPE_CHECKING:
    from ..models import Result

logger = logging.getLogger(__name__)


class TranscribeError(Exception):
    pass


def _round_to_field_precision(
    value: Decimal,
    model: type,
    field_name: str,
) -> Decimal:
    """Round a Decimal to the decimal_places defined on the model field."""
    try:
        field = model._meta.get_field(field_name)
        dp = field.decimal_places
    except Exception:
        return value
    if dp is None:
        return value
    quantize_str = Decimal(10) ** -dp
    return value.quantize(quantize_str, rounding=ROUND_HALF_UP)


def _get_result_value(result: Result) -> tuple[Decimal | None, str]:
    """Return (value, units) preferring converted values."""
    if result.converted_result_value is not None:
        return result.converted_result_value, result.converted_units or ""
    return result.result_value, result.units or ""


def _make_detail(
    result: Result,
    panel_name: str,
    status: str,
    imported_value: Decimal | None = None,
    imported_units: str = "",
    existing_value: Decimal | None = None,
    existing_units: str = "",
    message: str = "",
) -> TranscribeDetail:
    return TranscribeDetail(
        subject_identifier=result.subject_identifier,
        visit_code=result.visit_code or "",
        visit_code_sequence=result.visit_code_sequence or 0,
        panel_name=panel_name,
        utest_id=result.utest_id,
        status=status,
        imported_value=imported_value,
        imported_units=imported_units,
        existing_value=existing_value,
        existing_units=existing_units,
        message=message,
    )


def _create_crf_instance(
    crf_info: CrfInfo,
    subject_visit: object,
    requisition: object,
) -> object:
    """Create a new CRF instance linked to the given requisition.

    Sets required fields to initial values. The CRF's save() will
    recalculate summary fields.
    """
    crf = crf_info.model(
        subject_visit=subject_visit,
        requisition=requisition,
        report_datetime=subject_visit.report_datetime,
        assay_datetime=requisition.drawn_datetime or subject_visit.report_datetime,
        results_abnormal=NO,
        results_reportable=NOT_APPLICABLE,
    )
    return crf


def _flag_discrepancy(crf: object, line: str) -> None:
    """Flag the CRF and append a discrepancy line, avoiding duplicates."""
    if not hasattr(crf, "crf_status_comments"):
        return
    crf.crf_status = CRF_ISSUE_DETECTED
    existing = crf.crf_status_comments or ""
    existing_lines = set(existing.splitlines())
    if line not in existing_lines:
        if existing.strip():
            crf.crf_status_comments = f"{existing.rstrip()}\n{line}"
        else:
            crf.crf_status_comments = line


def _transcribe_to_crf(
    crf: object,
    results: list[Result],
    panel_name: str,
    summary: TranscribeSummary,
    dry_run: bool,
) -> bool:
    """Transcribe result values onto CRF fields.

    Returns True if any fields were modified.
    """
    modified = False
    for result in results:
        utest_id = result.utest_id
        value_field = f"{utest_id}_value"
        units_field = f"{utest_id}_units"

        if not hasattr(crf, value_field):
            summary.add(
                _make_detail(
                    result,
                    panel_name,
                    "skipped",
                    message=f"Field '{value_field}' not found on CRF model.",
                )
            )
            continue

        imported_value, imported_units = _get_result_value(result)

        if imported_value is None:
            summary.add(
                _make_detail(
                    result,
                    panel_name,
                    "skipped",
                    message="No result value to transcribe.",
                )
            )
            continue

        # Round imported value to match the CRF field's decimal_places
        rounded_value = _round_to_field_precision(
            imported_value, type(crf), value_field
        )

        existing_value = getattr(crf, value_field, None)
        existing_units = getattr(crf, units_field, "") or ""

        if existing_value is not None:
            if existing_value == rounded_value:
                summary.add(
                    _make_detail(
                        result,
                        panel_name,
                        "already_correct",
                        imported_value=rounded_value,
                        imported_units=imported_units,
                        existing_value=existing_value,
                        existing_units=existing_units,
                    )
                )
            else:
                discrepancy_msg = (
                    f"Existing={existing_value} {existing_units}, "
                    f"Imported={rounded_value} {imported_units}"
                )
                summary.add(
                    _make_detail(
                        result,
                        panel_name,
                        "discrepancy",
                        imported_value=rounded_value,
                        imported_units=imported_units,
                        existing_value=existing_value,
                        existing_units=existing_units,
                        message=discrepancy_msg,
                    )
                )
                # Flag the CRF with a discrepancy comment
                comment_line = (
                    f"{panel_name}/{utest_id}: {discrepancy_msg}"
                )
                _flag_discrepancy(crf, comment_line)
                modified = True
            continue

        # Field is blank — transcribe
        if not dry_run:
            setattr(crf, value_field, rounded_value)
            if imported_units and hasattr(crf, units_field):
                setattr(crf, units_field, imported_units)
        modified = True
        summary.add(
            _make_detail(
                result,
                panel_name,
                "transcribed",
                imported_value=rounded_value,
                imported_units=imported_units,
            )
        )
    return modified


_VENDOR_FIELD_MAP: dict[str, str] = {
    "laboratory_id": "laboratory",
    "order_number": "order_no",
    "order_datetime": "order_datetime",
    "result_number": "result_no",
    "result_datetime": "result_datetime",
    "specimen_number": "sample_no",
    "specimen_received_datetime": "specimen_received_datetime",
}


def _update_requisition_vendor_fields(
    requisition: object,
    results: list[Result],
) -> None:
    """Populate blank vendor fields on the requisition from imported results.

    Only sets fields that are currently empty/null. Uses the first
    non-empty value found across the results in the group.
    """
    ref = results[0] if results else None
    if not ref:
        return
    updated_fields: list[str] = []
    for req_field, result_attr in _VENDOR_FIELD_MAP.items():
        if not hasattr(requisition, req_field):
            continue
        current = getattr(requisition, req_field, None)
        if current not in (None, ""):
            continue
        value = next(
            (getattr(r, result_attr) for r in results if getattr(r, result_attr, None)),
            None,
        )
        if value is not None:
            setattr(requisition, req_field, value)
            updated_fields.append(req_field)
    if not requisition.resulted:
        requisition.resulted = True
        updated_fields.append("resulted")
    if updated_fields:
        requisition.save(update_fields=updated_fields)


def transcribe_results(
    results_qs: QuerySet,
    *,
    dry_run: bool = False,
) -> TranscribeSummary:
    """Transcribe imported Result rows onto their corresponding CRF models.

    Groups results by (subject_identifier, visit_code, visit_code_sequence),
    resolves SubjectVisit → SubjectRequisition → CRF, and populates blank
    fields. Existing values are never overwritten; discrepancies are flagged.
    """
    summary = TranscribeSummary()

    # Build discovery maps
    crf_models = discover_crf_models()
    utest_to_panel = build_utest_to_panel_map(crf_models)

    SubjectVisit = apps.get_model(settings.SUBJECT_VISIT_MODEL)
    SubjectRequisition = apps.get_model(
        settings.SUBJECT_REQUISITION_MODEL
    )

    # Filter to results that have utest_id and subject_identifier + visit_code
    workable = results_qs.filter(
        utest_id__gt="",
        subject_identifier__gt="",
        visit_code__gt="",
    )

    # Group by (subject_identifier, visit_code, visit_code_sequence)
    groups: dict[tuple, list[Result]] = defaultdict(list)
    for result in workable:
        key = (
            result.subject_identifier,
            result.visit_code,
            result.visit_code_sequence or 0,
        )
        groups[key].append(result)

    now = timezone.now()

    for (subject_id, visit_code, visit_code_seq), results in groups.items():
        # Look up SubjectVisit
        subject_visit = (
            SubjectVisit.objects.filter(
                subject_identifier=subject_id,
                appointment__visit_code=visit_code,
                appointment__visit_code_sequence=visit_code_seq,
            ).first()
        )
        if not subject_visit:
            summary.no_visit += 1
            for r in results:
                summary.add(
                    _make_detail(
                        r,
                        utest_to_panel.get(r.utest_id, "?"),
                        "skipped",
                        message="SubjectVisit not found.",
                    )
                )
            continue

        # Sub-group results by panel
        panel_groups: dict[str, list[Result]] = defaultdict(list)
        for result in results:
            panel_name = utest_to_panel.get(result.utest_id)
            if not panel_name:
                summary.add(
                    _make_detail(
                        result,
                        "?",
                        "skipped",
                        message=f"utest_id '{result.utest_id}' not mapped to any panel.",
                    )
                )
                continue
            panel_groups[panel_name].append(result)

        for panel_name, panel_results in panel_groups.items():
            crf_info = crf_models.get(panel_name)
            if not crf_info:
                for r in panel_results:
                    summary.add(
                        _make_detail(
                            r,
                            panel_name,
                            "skipped",
                            message=f"No CRF model found for panel '{panel_name}'.",
                        )
                    )
                continue

            # Look up SubjectRequisition
            requisition = (
                SubjectRequisition.objects.filter(
                    subject_visit=subject_visit,
                    panel__name=panel_name,
                ).first()
            )
            if not requisition:
                summary.no_requisition += 1
                for r in panel_results:
                    summary.add(
                        _make_detail(
                            r,
                            panel_name,
                            "skipped",
                            message="SubjectRequisition not found.",
                        )
                    )
                continue

            # Look up or create CRF instance
            crf = (
                crf_info.model.objects.filter(requisition=requisition).first()
            )
            created = False
            if not crf:
                if dry_run:
                    # Simulate creation for reporting
                    summary.crf_created += 1
                    crf = crf_info.model(
                        subject_visit=subject_visit,
                        requisition=requisition,
                    )
                else:
                    crf = _create_crf_instance(crf_info, subject_visit, requisition)
                    created = True

            modified = _transcribe_to_crf(
                crf, panel_results, panel_name, summary, dry_run
            )

            if not dry_run:
                if modified or created:
                    crf.save()
                    if created:
                        summary.crf_created += 1
                    # Reset clinic verification if CRF values were changed
                    if (
                        modified
                        and hasattr(requisition, "clinic_verified")
                        and requisition.clinic_verified != NO
                    ):
                        requisition.clinic_verified = NO
                        requisition.clinic_verified_datetime = None
                        requisition.save(
                            update_fields=[
                                "clinic_verified",
                                "clinic_verified_datetime",
                            ]
                        )
                    # Mark results as transcribed
                    result_pks = [r.pk for r in panel_results if r.utest_id]
                    ResultModel.objects.filter(
                        pk__in=result_pks,
                        transcribed_datetime__isnull=True,
                    ).update(transcribed_datetime=now)
                # Always update requisition vendor fields
                _update_requisition_vendor_fields(requisition, panel_results)

    return summary
