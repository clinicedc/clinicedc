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
from collections import Counter
from collections.abc import Callable, Iterator
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

from edc_identifier.checkdigit_mixins import LuhnMixin
from edc_lab import site_labs
from edc_lab.utils import get_requisition_model
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_registration.models import RegisteredSubject
from edc_reportable.models import NormalData
from edc_screening.utils import get_subject_screening_model_cls
from edc_sites.site import sites

from .constants import (
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
    LINKED,
    NO_MATCH,
    NO_PANEL_FOR_UTEST_ID,
    NO_UTEST_ID,
    OUT_OF_SCOPE,
    REASON_BAD_CHECK_DIGIT,
    REASON_FOREIGN,
    REASON_INVALID_SCREENING,
    REASON_UNREGISTERED_SITE,
    REASON_VALID_SCREENING,
    REASON_VALID_SUBJECT,
    SUBJECT_NOT_FOUND,
)
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
    skipped_out_of_scope: int = 0  # not stored (EDC_LAB_RESULTS_SKIP_OUT_OF_SCOPE)
    unresolved: int = 0  # total unresolved (subject_not_found + out_of_scope)
    subject_not_found: int = 0  # reissue-able (this protocol/site, or screening)
    out_of_scope: int = 0  # wrong protocol / unregistered site / junk
    reasons: Counter = field(default_factory=Counter)
    unrecognized_units: set[tuple[str, str]] = field(default_factory=set)


@dataclass
class LinkSummary:
    linked: int = 0
    ambiguous: int = 0
    no_match: int = 0
    untracked: int = 0  # utest_id not on any panel
    unmapped: int = 0  # no EDC utest_id at all


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


def _registered_site_ids() -> set[int]:
    return {single_site.site_id for single_site in sites.all(aslist=True)}


def _screening_exists(screening_identifier: str) -> bool:
    return (
        get_subject_screening_model_cls()
        .objects.filter(screening_identifier=screening_identifier)
        .exists()
    )


def _classify_subject_identifier(extracted: str) -> str:
    """Reason for a value that matches the subject_identifier pattern:
    UNREGISTERED_SITE / BAD_CHECK_DIGIT / VALID_SUBJECT (FOREIGN if malformed).
    """
    # pattern guarantees protocol-site-sequence-checkdigit numeric segments
    parts = extracted.split("-")
    try:
        site_id = int(parts[1])
    except (IndexError, ValueError):
        return REASON_FOREIGN
    if site_id not in _registered_site_ids():
        return REASON_UNREGISTERED_SITE
    if LuhnMixin().calculate_checkdigit("".join(parts[:-1])) != parts[-1]:
        return REASON_BAD_CHECK_DIGIT
    return REASON_VALID_SUBJECT


def classify_identifier(extracted: str) -> str:
    """Classify an extracted identifier against this deployment's rules.

    All rules are sourced from config/registry (no hardcoding):
    ``ResearchProtocolConfig`` for the subject/screening patterns and
    protocol number, ``edc_sites`` for registered sites, the Luhn check
    digit, and ``SubjectScreening`` for screening membership. Returns one
    of the ``REASON_*`` codes.
    """
    cfg = ResearchProtocolConfig()
    if re.search(cfg.subject_identifier_pattern, extracted):
        return _classify_subject_identifier(extracted)
    screening = extracted.replace("-", "")
    if re.fullmatch(cfg.screening_identifier_pattern, screening):
        # screening-shaped, but only "valid" if it is a known SubjectScreening;
        # otherwise it's a mistyped screening identifier (reissue-able).
        return (
            REASON_VALID_SCREENING
            if _screening_exists(screening)
            else REASON_INVALID_SCREENING
        )
    return REASON_FOREIGN


# Reasons that mean "this is (or should be) one of ours" -> reissue / review.
_REISSUEABLE_REASONS = frozenset(
    {
        REASON_VALID_SUBJECT,
        REASON_BAD_CHECK_DIGIT,
        REASON_VALID_SCREENING,
        REASON_INVALID_SCREENING,
    }
)


def category_for_unresolved(name_id: str) -> tuple[str, str]:
    """Category + reason for an unresolved name_id.

    Returns (category, reason). A well-formed in-scope identifier (right
    protocol + registered site, or a screening identifier) is reissue-able
    -> SUBJECT_NOT_FOUND. Wrong protocol / unregistered site / junk is
    OUT_OF_SCOPE.
    """
    reason = classify_identifier(_extract_subject_identifier(name_id))
    if reason in _REISSUEABLE_REASONS:
        return SUBJECT_NOT_FOUND, reason
    return OUT_OF_SCOPE, reason


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
        Laboratory name (key into ``EDC_LAB_RESULTS_PARSERS``).
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
        parsers: dict[str, str] = getattr(settings, "EDC_LAB_RESULTS_PARSERS", {})
        dotted_path = parsers.get(self.laboratory)
        if not dotted_path:
            available = ", ".join(sorted(parsers.keys())) or "(none)"
            raise LabResultImportError(
                f"No parser configured for laboratory '{self.laboratory}'. "
                f"Available: {available}. "
                f"Check EDC_LAB_RESULTS_PARSERS in settings."
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
            settings, "EDC_LAB_RESULTS_DEFAULT_MAPPINGS", {}
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
        category_cache: dict[str, tuple[str, str]] = {}
        skip_out_of_scope = getattr(
            settings, "EDC_LAB_RESULTS_SKIP_OUT_OF_SCOPE", False
        )
        skipped = 0
        skipped_out_of_scope = 0
        unresolved_count = 0
        subject_not_found_count = 0
        out_of_scope_count = 0
        reasons: Counter = Counter()
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
            if resolution.resolved:
                match_category, match_comment = "", ""
            else:
                unresolved_count += 1
                if name_id not in category_cache:
                    category_cache[name_id] = category_for_unresolved(name_id)
                match_category, match_comment = category_cache[name_id]
                if match_category == SUBJECT_NOT_FOUND:
                    subject_not_found_count += 1
                else:
                    out_of_scope_count += 1
                reasons[match_comment] += 1
                if skip_out_of_scope and match_category == OUT_OF_SCOPE:
                    # governance: do not persist another protocol's data here
                    skipped_out_of_scope += 1
                    continue

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
            converted_value, converted_units = self._convert_result(
                utest_id, result_value, units, units_cache, unrecognized_units
            )

            batch.append(
                self._build_result(
                    unique_values,
                    row,
                    resolution,
                    match_category,
                    match_comment,
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
            created=len(df) - skipped - skipped_out_of_scope,
            skipped=skipped,
            skipped_out_of_scope=skipped_out_of_scope,
            unresolved=unresolved_count,
            subject_not_found=subject_not_found_count,
            out_of_scope=out_of_scope_count,
            reasons=reasons,
            unrecognized_units=unrecognized_units,
        )

    @staticmethod
    def _convert_result(
        utest_id: str,
        result_value: Decimal | None,
        units: str,
        units_cache: dict,
        unrecognized_units: set[tuple[str, str]],
    ) -> tuple[Decimal | None, str]:
        """Convert to reportable units; record units with no conversion path."""
        converted_value, converted_units = attempt_conversion(
            utest_id, result_value, units, units_cache=units_cache
        )
        if (
            utest_id
            and result_value is not None
            and units
            and converted_value is None
            and normalize_units(units) not in units_cache.get(utest_id, [])
        ):
            unrecognized_units.add((utest_id, units))
        return converted_value, converted_units

    def _build_result(
        self,
        unique_values: tuple[Any, ...],
        row: pd.Series,
        resolution: SubjectResolution,
        match_category: str,
        match_comment: str,
        utest_id: str,
        result_value: Decimal | None,
        units: str,
        converted_value: Decimal | None,
        converted_units: str,
    ) -> Result:
        return Result(
            laboratory=self.laboratory,
            order_no=unique_values[0],
            result_no=unique_values[1],
            sample_no=unique_values[2],
            investigation=unique_values[3],
            report_datetime=unique_values[4],
            name_id=unique_values[5],
            subject_identifier=resolution.subject_identifier,
            screening_identifier=resolution.screening_identifier,
            subject_not_found=not resolution.resolved,
            requisition_match_category=match_category,
            requisition_match_comment=match_comment,
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
    def _iter_panel_utest_ids(utest_ids: Any) -> Iterator[str]:
        """Yield the reported utest_id for each entry in a panel's
        ``utest_ids``. Entries may be a plain utest_id or a tuple whose
        first element is the (derived) utest_id.
        """
        for entry in utest_ids or ():
            if isinstance(entry, (tuple, list)):
                if entry:
                    yield entry[0]
            else:
                yield entry

    @classmethod
    def _build_utest_id_panel_index(cls) -> dict[str, set[str]]:
        """Map each utest_id to the set of panel names that report it,
        derived from the registered lab profiles (``site_labs``).

        A project may attach extra utest_ids to a registered panel via
        ``settings.EDC_LAB_RESULTS_UTEST_PANELS`` ({utest_id: panel_name}),
        e.g. FBC differentials -> "fbc", so those results link to that
        panel's requisition instead of being untracked. Entries pointing to
        an unregistered panel name are ignored.
        """
        index: dict[str, set[str]] = {}
        registered_panels: set[str] = set()
        for lab_profile in site_labs.lab_profiles.values():
            for panel in lab_profile.panels.values():
                registered_panels.add(panel.name)
                for utest_id in cls._iter_panel_utest_ids(panel.utest_ids):
                    index.setdefault(utest_id, set()).add(panel.name)
        extra: dict[str, str] = getattr(settings, "EDC_LAB_RESULTS_UTEST_PANELS", {})
        for utest_id, panel_name in extra.items():
            if panel_name in registered_panels:
                index.setdefault(utest_id, set()).add(panel_name)
        return index

    @classmethod
    def link_requisitions(cls) -> LinkSummary:
        """Populate requisition_identifier / visit_code / visit_code_sequence
        on unlinked Results.

        A result can only be matched by panel: its utest_id must resolve to a
        registered panel. If it does not, no requisition can own it, so it is
        categorized (NO_UTEST_ID when unmapped, NO_PANEL_FOR_UTEST_ID when the
        utest_id is an untracked analyte) and left unlinked -- we deliberately
        do NOT fall back to matching on day alone, which would manufacture
        false ambiguity against every same-day requisition.

        For a panel-resolvable result, candidates are keyed by
        subject_identifier and same calendar day (order_datetime vs
        drawn_datetime) and filtered to the requisition whose panel reports
        that utest_id. Exactly one candidate -> linked; more than one ->
        flagged requisition_ambiguous for manual review; none -> NO_MATCH.

        In every case the outcome is recorded on the Result via
        requisition_match_category, a human-readable requisition_match_comment,
        and, for ambiguous matches, the contending requisition_candidates -- so
        review can act without recomputing.
        """
        unlinked = Result.objects.filter(
            requisition_identifier="",
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
            .select_related("panel", "subject_visit")
        ):
            key = (
                req.subject_identifier,
                req.drawn_datetime.date().isoformat(),
            )
            req_by_key.setdefault(key, []).append(req)

        panel_index = cls._build_utest_id_panel_index()

        linked = 0
        ambiguous = 0
        no_match = 0
        untracked = 0
        unmapped = 0
        no_match_pks: list = []
        no_panel_pks: list = []
        no_utest_id_pks: list = []
        # (pk, visit_code, visit_code_sequence, requisition_identifier)
        link_updates: list[tuple[Any, str, int, str]] = []
        # (pk, category, comment, candidate_identifiers)
        ambiguous_updates: list[tuple[Any, str, str, list[str]]] = []

        for result in unlinked.iterator():
            utest_id = result.utest_id
            if not utest_id:
                # No EDC utest_id mapping at all -> cannot match by panel.
                unmapped += 1
                no_utest_id_pks.append(result.pk)
                continue

            panel_names = panel_index.get(utest_id)
            if not panel_names:
                # utest_id is not on any registered panel (an untracked lab
                # analyte). Do NOT fall back to day-only matching -- that
                # manufactures false ambiguity against every same-day
                # requisition. Record it as untracked and move on.
                untracked += 1
                no_panel_pks.append(result.pk)
                continue

            key = (
                result.subject_identifier,
                result.order_datetime.date().isoformat(),
            )
            candidates = [
                req
                for req in req_by_key.get(key, [])
                if req.panel and req.panel.name in panel_names
            ]

            count = len(candidates)
            if count == 0:
                no_match += 1
                no_match_pks.append(result.pk)
            elif count > 1:
                ambiguous += 1
                ambiguous_updates.append(cls._describe_ambiguity(result, candidates))
            else:
                req = candidates[0]
                link_updates.append(
                    (
                        result.pk,
                        req.visit_code,
                        req.visit_code_sequence,
                        req.requisition_identifier,
                    )
                )
                linked += 1

        cls._apply_category(no_utest_id_pks, NO_UTEST_ID)
        cls._apply_category(no_panel_pks, NO_PANEL_FOR_UTEST_ID)
        cls._apply_category(no_match_pks, NO_MATCH)
        cls._apply_ambiguous(ambiguous_updates)
        cls._apply_linked(link_updates)

        return LinkSummary(
            linked=linked,
            ambiguous=ambiguous,
            no_match=no_match,
            untracked=untracked,
            unmapped=unmapped,
        )

    @staticmethod
    def _describe_ambiguity(result, candidates) -> tuple[Any, str, str, list[str]]:
        """Classify an ambiguous match and capture its contending
        requisitions for later review. Returns
        (pk, category, comment, candidate_identifiers).
        """
        distinct_panels = sorted({r.panel.name for r in candidates if r.panel})
        category = (
            AMBIGUOUS_MULTI_PANEL if len(distinct_panels) > 1 else AMBIGUOUS_SAME_PANEL
        )
        candidate_ids = [r.requisition_identifier for r in candidates]
        comment = (
            f"{len(candidates)} candidate requisition(s) on "
            f"{result.order_datetime.date().isoformat()}; "
            f"panel(s): {', '.join(distinct_panels) or '(none)'}."
        )
        return result.pk, category, comment, candidate_ids

    @staticmethod
    def _apply_linked(link_updates: list[tuple[Any, str, int, str]]) -> None:
        if not link_updates:
            return
        objs = {
            r.pk: r for r in Result.objects.filter(pk__in=[u[0] for u in link_updates])
        }
        for pk, vc, vcs, req_id in link_updates:
            obj = objs[pk]
            obj.visit_code = vc
            obj.visit_code_sequence = vcs
            obj.requisition_identifier = req_id
            # Clear any stale ambiguity carried from a prior day-only run.
            obj.requisition_ambiguous = False
            obj.requisition_match_category = LINKED
            obj.requisition_match_comment = ""
            obj.requisition_candidates = []
        Result.objects.bulk_update(
            objs.values(),
            [
                "visit_code",
                "visit_code_sequence",
                "requisition_identifier",
                "requisition_ambiguous",
                "requisition_match_category",
                "requisition_match_comment",
                "requisition_candidates",
            ],
            batch_size=500,
        )

    @staticmethod
    def _apply_ambiguous(
        ambiguous_updates: list[tuple[Any, str, str, list[str]]],
    ) -> None:
        if not ambiguous_updates:
            return
        objs = {
            r.pk: r
            for r in Result.objects.filter(pk__in=[u[0] for u in ambiguous_updates])
        }
        for pk, category, comment, candidate_ids in ambiguous_updates:
            obj = objs[pk]
            obj.requisition_ambiguous = True
            obj.requisition_match_category = category
            obj.requisition_match_comment = comment
            obj.requisition_candidates = candidate_ids
        Result.objects.bulk_update(
            objs.values(),
            [
                "requisition_ambiguous",
                "requisition_match_category",
                "requisition_match_comment",
                "requisition_candidates",
            ],
            batch_size=500,
        )

    @staticmethod
    def _apply_category(pks: list, category: str) -> None:
        """Bulk-set a terminal, non-linked category (no requisition, no
        candidates) on the given results.
        """
        if not pks:
            return
        Result.objects.filter(pk__in=pks).update(
            requisition_ambiguous=False,
            requisition_match_category=category,
            requisition_match_comment="",
            requisition_candidates=[],
        )
