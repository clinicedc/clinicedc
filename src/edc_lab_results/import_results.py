"""Core logic for importing lab results into the EDC.

The ``LabResultImporter`` class can be used from a management command,
a Django view, a Jupyter notebook, or any other context::

    from edc_lab_results.import_results import LabResultImporter

    importer = LabResultImporter("MNH")
    df = importer.parse(folder, tz=tz)
    utest_map = importer.resolve_mappings(df)
    save_summary = importer.save_results(df, utest_map)
    link_summary = importer.link_requisitions()
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from importlib import import_module
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
from clinicedc_constants import UUID_PATTERN
from django.conf import settings
from parse_trial_labs import parse_folder as _parse_folder
from tqdm import tqdm

from edc_lab.utils import get_requisition_model
from edc_registration.models import RegisteredSubject
from edc_reportable.models import NormalData

from .models import InvestigationMapping, Result
from .unit_conversion import (
    attempt_conversion,
    build_normal_data_units_cache,
    normalize_units,
)


class LabResultImportError(Exception):
    pass


@dataclass
class SaveSummary:
    created: int = 0
    skipped: int = 0
    unresolved: int = 0
    unrecognized_units: set[tuple[str, str]] = field(default_factory=set)


@dataclass
class LinkSummary:
    linked: int = 0
    ambiguous: int = 0
    no_match: int = 0


@dataclass
class MappingSummary:
    utest_map: dict[str, str] = field(default_factory=dict)
    mapped: int = 0
    unmapped: int = 0
    not_in_reportable: list[tuple[str, str]] = field(default_factory=list)


class SubjectResolution:
    """Result of attempting to resolve a name_id to a registered
    subject.
    """

    __slots__ = ("resolved", "screening_identifier", "subject_identifier")

    def __init__(
        self,
        subject_identifier: str = "",
        screening_identifier: str = "",
        *,
        resolved: bool = False,
    ) -> None:
        self.subject_identifier = subject_identifier
        self.screening_identifier = screening_identifier
        self.resolved = resolved


def _to_datetime(value: object) -> object | None:
    if value is None or pd.isna(value):
        return None
    return value


def _to_decimal(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _extract_subject_identifier(name_id: str) -> str:
    if "/" in name_id:
        name_id = name_id.replace("//", "/")
        return name_id.split("/", 1)[1]
    return name_id


def resolve_subject(
    name_id: str,
    *,
    cache: dict[str, SubjectResolution],
) -> SubjectResolution:
    """Resolve name_id to a subject_identifier or screening_identifier.

    Tries subject_identifier first, then screening_identifier
    (stored without dash). Returns a SubjectResolution with
    resolved=False if neither matches.
    """
    if name_id in cache:
        return cache[name_id]

    extracted = _extract_subject_identifier(name_id)
    if not extracted:
        result = SubjectResolution()
        cache[name_id] = result
        return result

    # Try subject_identifier first
    if RegisteredSubject.objects.filter(subject_identifier=extracted).exists():
        result = SubjectResolution(subject_identifier=extracted, resolved=True)
        cache[name_id] = result
        return result

    # Try screening_identifier (strip dash for DB lookup)
    screening_no_dash = extracted.replace("-", "")
    try:
        rs = RegisteredSubject.objects.get(screening_identifier=screening_no_dash)
    except RegisteredSubject.DoesNotExist:
        pass
    else:
        sid = rs.subject_identifier
        # If subject_identifier is still a UUID, the subject hasn't
        # consented yet — store screening_identifier only.
        if re.match(UUID_PATTERN, sid):
            sid = ""
        result = SubjectResolution(
            subject_identifier=sid,
            screening_identifier=screening_no_dash,
            resolved=True,
        )
        cache[name_id] = result
        return result

    # Not resolved
    result = SubjectResolution()
    cache[name_id] = result
    return result


def best_guess_utest_id(
    investigation: str,
    known_utest_ids: set[str],
    default_mappings: dict[str, str],
) -> str:
    if investigation in default_mappings:
        return default_mappings[investigation]
    candidates = list(known_utest_ids)
    matches = get_close_matches(investigation.lower(), candidates, n=1, cutoff=0.5)
    return matches[0] if matches else ""


def check_utest_id_conflict(utest_id: str, investigation: str, laboratory: str) -> str | None:
    """Return the conflicting investigation name, or None."""
    if not utest_id:
        return None
    try:
        existing = InvestigationMapping.objects.get(laboratory=laboratory, utest_id=utest_id)
    except InvestigationMapping.DoesNotExist:
        return None
    if existing.investigation != investigation:
        return existing.investigation
    return None


class LabResultImporter:
    """Encapsulates the full lab-result import pipeline.

    Parameters
    ----------
    laboratory
        Laboratory name (key into ``EDC_LAB_PARSERS``).
    prompt_func
        Optional callback ``(investigation, guess, laboratory) -> utest_id``
        called when an investigation has no saved mapping.  If *None*,
        unknown investigations are left unmapped (empty ``utest_id``).
    """

    def __init__(
        self,
        laboratory: str,
        *,
        prompt_func: Callable[[str, str, str], str] | None = None,
    ) -> None:
        self.laboratory = laboratory
        self.prompt_func = prompt_func

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def resolve_parser(self) -> Callable:
        """Return the parser callable for this laboratory."""
        parsers: dict[str, str] = getattr(settings, "EDC_LAB_PARSERS", {})
        dotted_path = parsers.get(self.laboratory)
        if not dotted_path:
            available = ", ".join(sorted(parsers.keys())) or "(none)"
            raise LabResultImportError(
                f"No parser configured for laboratory '{self.laboratory}'. "
                f"Available: {available}. "
                f"Check EDC_LAB_PARSERS in settings."
            )
        module_path, func_name = dotted_path.rsplit(".", 1)
        try:
            module = import_module(module_path)
        except ModuleNotFoundError as e:
            raise LabResultImportError(
                f"Cannot import parser module '{module_path}': {e}"
            ) from e
        func = getattr(module, func_name, None)
        if func is None:
            raise LabResultImportError(
                f"Parser module '{module_path}' has no attribute '{func_name}'."
            )
        return func

    def parse(
        self,
        folder: str | Path,
        *,
        tz: ZoneInfo | None = None,
        output_path: str | Path | None = None,
    ) -> pd.DataFrame:
        """Parse PDF files and optionally save a CSV."""
        folder = Path(folder).expanduser()
        if not folder.is_dir():
            raise LabResultImportError(f"Not a directory: {folder}")

        pdf_count = len(list(folder.glob("*.pdf")))
        if pdf_count == 0:
            raise LabResultImportError(f"No PDF files found in {folder}")

        parser_func = self.resolve_parser()
        df: pd.DataFrame = _parse_folder(folder, parser_func, tz=tz)

        if not df.empty and output_path:
            Path(output_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)

        return df

    def parse_files(
        self,
        file_paths: list[Path],
        *,
        tz: ZoneInfo | None = None,
    ) -> pd.DataFrame:
        """Parse specific PDF files (used for pending uploads)."""
        parser_func = self.resolve_parser()
        all_rows: list[dict] = []
        for pdf_path in file_paths:
            all_rows.extend(parser_func(pdf_path, tz=tz))
        df = pd.DataFrame(all_rows)
        if not df.empty:
            df["result"] = pd.to_numeric(df["result"], errors="coerce")
        return df

    # ------------------------------------------------------------------
    # Investigation mapping
    # ------------------------------------------------------------------

    def resolve_mappings(
        self,
        df: pd.DataFrame,
    ) -> MappingSummary:
        """Resolve investigation → utest_id for every investigation
        in *df*.

        Already-persisted mappings are reused.  Unknown investigations
        are delegated to ``self.prompt_func`` if set; otherwise they
        are left unmapped.
        """
        known_utest_ids = set(NormalData.objects.values_list("label", flat=True).distinct())
        default_mappings: dict[str, str] = getattr(
            settings, "EDC_LAB_DEFAULT_MAPPINGS", {}
        ).get(self.laboratory, {})

        investigations = list(df["investigation"].unique())
        utest_map: dict[str, str] = {}

        for inv in sorted(investigations):
            utest_map[inv] = self._resolve_single_mapping(
                inv, known_utest_ids, default_mappings
            )

        not_in_reportable = [
            (m.investigation, m.utest_id)
            for m in InvestigationMapping.objects.filter(
                laboratory=self.laboratory, in_reportable=False
            ).exclude(utest_id="")
        ]

        return MappingSummary(
            utest_map=utest_map,
            mapped=sum(1 for v in utest_map.values() if v),
            unmapped=sum(1 for v in utest_map.values() if not v),
            not_in_reportable=not_in_reportable,
        )

    def _resolve_single_mapping(
        self,
        investigation: str,
        known_utest_ids: set[str],
        default_mappings: dict[str, str],
    ) -> str:
        try:
            mapping = InvestigationMapping.objects.get(
                laboratory=self.laboratory, investigation=investigation
            )
        except InvestigationMapping.DoesNotExist:
            pass
        else:
            return mapping.utest_id

        guess = best_guess_utest_id(investigation, known_utest_ids, default_mappings)

        if self.prompt_func:
            utest_id = self.prompt_func(investigation, guess, self.laboratory)
        elif guess:
            utest_id = guess
        else:
            utest_id = ""

        in_reportable = bool(utest_id and NormalData.objects.filter(label=utest_id).exists())

        InvestigationMapping.objects.create(
            laboratory=self.laboratory,
            investigation=investigation,
            utest_id=utest_id,
            in_reportable=in_reportable,
        )
        return utest_id

    # ------------------------------------------------------------------
    # Saving results
    # ------------------------------------------------------------------

    def save_results(
        self,
        df: pd.DataFrame,
        utest_map: dict[str, str],
        *,
        batch_size: int = 500,
    ) -> SaveSummary:
        """Bulk-create ``Result`` rows from *df*."""
        subject_cache: dict[str, SubjectResolution] = {}
        skipped = 0
        unresolved_count = 0
        unrecognized_units: set[tuple[str, str]] = set()

        existing_keys = set(
            Result.objects.values_list(
                "order_no",
                "result_no",
                "sample_no",
                "investigation",
                "report_datetime",
                "name_id",
            )
        )
        units_cache = build_normal_data_units_cache()
        batch: list[Result] = []

        for _, row in tqdm(df.iterrows(), total=len(df)):
            name_id = row.get("name_id", "")
            resolution = resolve_subject(name_id, cache=subject_cache)
            if not resolution.resolved:
                unresolved_count += 1

            unique_values = (
                row.get("order_no", ""),
                row.get("result_no", ""),
                row.get("sample_no", ""),
                row.get("investigation", ""),
                _to_datetime(row.get("reported_datetime")),
                name_id,
            )
            if unique_values in existing_keys:
                skipped += 1
                continue
            existing_keys.add(unique_values)

            investigation = row.get("investigation", "")
            utest_id = utest_map.get(investigation, "")
            result_value = _to_decimal(row.get("result", ""))
            units = row.get("units", "")

            converted_value, converted_units = attempt_conversion(
                utest_id, result_value, units, units_cache=units_cache
            )

            if utest_id and result_value is not None and units and converted_value is None:
                normalized = normalize_units(units)
                available = units_cache.get(utest_id, [])
                if normalized not in available:
                    unrecognized_units.add((utest_id, units))

            batch.append(
                self._build_result(
                    unique_values,
                    row,
                    resolution,
                    utest_id,
                    result_value,
                    units,
                    converted_value,
                    converted_units,
                )
            )
            if len(batch) >= batch_size:
                Result.objects.bulk_create(batch)
                batch.clear()

        if batch:
            Result.objects.bulk_create(batch)

        return SaveSummary(
            created=len(df) - skipped,
            skipped=skipped,
            unresolved=unresolved_count,
            unrecognized_units=unrecognized_units,
        )

    @staticmethod
    def _build_result(
        unique_values: tuple[Any, ...],
        row: pd.Series,
        resolution: SubjectResolution,
        utest_id: str,
        result_value: Decimal | None,
        units: str,
        converted_value: Decimal | None,
        converted_units: str,
    ) -> Result:
        return Result(
            order_no=unique_values[0],
            result_no=unique_values[1],
            sample_no=unique_values[2],
            investigation=unique_values[3],
            report_datetime=unique_values[4],
            name_id=unique_values[5],
            subject_identifier=resolution.subject_identifier,
            screening_identifier=resolution.screening_identifier,
            subject_not_found=not resolution.resolved,
            utest_id=utest_id,
            source_file=row.get("source_file", ""),
            report_type=row.get("report_type", ""),
            result_status=row.get("result_status", ""),
            age=(int(row["age"]) if row.get("age") else None),
            sex=row.get("sex", ""),
            ordered_by=row.get("ordered_by", ""),
            clinic_ward=row.get("clinic_ward", ""),
            order_datetime=_to_datetime(row.get("order_datetime")),
            result_datetime=_to_datetime(row.get("result_datetime")),
            specimen_collected_by=row.get("specimen_collected_by", ""),
            specimen_collected_datetime=_to_datetime(row.get("specimen_collected_datetime")),
            specimen_received_by=row.get("specimen_received_by", ""),
            specimen_received_datetime=_to_datetime(row.get("specimen_received_datetime")),
            sample_type=row.get("sample_type", ""),
            sample_condition=row.get("sample_condition", ""),
            priority=row.get("priority", ""),
            reported_by=row.get("reported_by", ""),
            verified_by=row.get("verified_by", ""),
            verified_datetime=_to_datetime(row.get("verified_datetime")),
            result_value=result_value,
            units=units,
            converted_result_value=converted_value,
            converted_units=converted_units,
            flag=row.get("flag", ""),
            reference_range_lower=_to_decimal(row.get("reference_range_lower", "")),
            reference_range_upper=_to_decimal(row.get("reference_range_upper", "")),
        )

    # ------------------------------------------------------------------
    # Requisition linking
    # ------------------------------------------------------------------

    @staticmethod
    def link_requisitions() -> LinkSummary:
        """Populate visit_code / visit_code_sequence on unlinked Results.

        Matches by subject_identifier and same calendar day
        (order_datetime vs drawn_datetime).  If multiple requisitions
        match the same day, the result is flagged as ambiguous and
        left unpopulated for manual review.
        """
        unlinked = Result.objects.filter(
            visit_code="",
            subject_not_found=False,
            order_datetime__isnull=False,
        ).exclude(subject_identifier="")

        if not unlinked.exists():
            return LinkSummary()

        # Only load requisitions for subjects that need linking
        subject_ids = set(
            unlinked.values_list("subject_identifier", flat=True).distinct()
        )

        requisition_model = get_requisition_model()
        req_by_key: dict[tuple[str, str], list] = {}
        for req in (
            requisition_model.objects.filter(
                drawn_datetime__isnull=False,
                subject_identifier__in=subject_ids,
            )
            .select_related("subject_visit")
        ):
            key = (
                req.subject_identifier,
                req.drawn_datetime.date().isoformat(),
            )
            req_by_key.setdefault(key, []).append(req)

        linked = 0
        ambiguous = 0
        no_match = 0
        ambiguous_pks: list = []
        updates: list[tuple[Any, str, int]] = []

        for result in unlinked.iterator():
            key = (
                result.subject_identifier,
                result.order_datetime.date().isoformat(),
            )
            candidates = req_by_key.get(key, [])
            count = len(candidates)
            if count == 0:
                no_match += 1
            elif count > 1:
                ambiguous_pks.append(result.pk)
                ambiguous += 1
            else:
                req = candidates[0]
                updates.append(
                    (
                        result.pk,
                        req.visit_code,
                        req.visit_code_sequence,
                    )
                )
                linked += 1

        if ambiguous_pks:
            Result.objects.filter(pk__in=ambiguous_pks).update(requisition_ambiguous=True)

        if updates:
            result_objs = {
                r.pk: r for r in Result.objects.filter(pk__in=[u[0] for u in updates])
            }
            for pk, vc, vcs in updates:
                obj = result_objs[pk]
                obj.visit_code = vc
                obj.visit_code_sequence = vcs
            Result.objects.bulk_update(
                result_objs.values(),
                ["visit_code", "visit_code_sequence"],
                batch_size=500,
            )

        return LinkSummary(linked=linked, ambiguous=ambiguous, no_match=no_match)
