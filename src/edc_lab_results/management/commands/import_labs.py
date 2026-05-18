"""Import lab results from a folder of PDF files.

The parser is resolved from the EDC_LAB_PARSERS setting,
keyed by laboratory name.

Usage::

    manage.py import_labs /path/to/pdf_folder --laboratory "MNH"
    manage.py import_labs /path/to/pdf_folder \
        --laboratory "MNH" --dry-run
    manage.py import_labs /path/to/pdf_folder \
        --laboratory "MNH" --output /path/to/output.csv
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from importlib import import_module
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from parse_trial_labs import parse_folder

from edc_lab_results.models import InvestigationMapping, Result
from edc_lab_results.unit_conversion import attempt_conversion, normalize_units
from edc_registration.models import RegisteredSubject
from edc_reportable.models import NormalData


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
        return name_id.split("/", 1)[1]
    return name_id


def _resolve_parser(laboratory: str) -> Callable:
    parsers = getattr(settings, "EDC_LAB_PARSERS", {})
    dotted_path = parsers.get(laboratory)
    if not dotted_path:
        available = ", ".join(sorted(parsers.keys())) or "(none)"
        raise CommandError(
            f"No parser configured for laboratory '{laboratory}'. "
            f"Available: {available}. "
            f"Check EDC_LAB_PARSERS in settings."
        )
    module_path, func_name = dotted_path.rsplit(".", 1)
    try:
        module = import_module(module_path)
    except ImportError as e:
        raise CommandError(f"Cannot import parser module '{module_path}': {e}") from e
    func = getattr(module, func_name, None)
    if func is None:
        raise CommandError(f"Parser module '{module_path}' has no attribute '{func_name}'.")
    return func


def _best_guess_utest_id(
    investigation: str,
    known_utest_ids: set[str],
    default_mappings: dict[str, str],
) -> str:
    if investigation in default_mappings:
        return default_mappings[investigation]
    candidates = list(known_utest_ids)
    matches = get_close_matches(investigation.lower(), candidates, n=1, cutoff=0.5)
    return matches[0] if matches else ""


def _utest_id_in_reportable(utest_id: str) -> bool:
    if not utest_id:
        return False
    return NormalData.objects.filter(label=utest_id).exists()


def _check_utest_id_conflict(utest_id: str, investigation: str, laboratory: str) -> str | None:
    if not utest_id:
        return None
    try:
        existing = InvestigationMapping.objects.get(laboratory=laboratory, utest_id=utest_id)
    except InvestigationMapping.DoesNotExist:
        return None
    if existing.investigation != investigation:
        return existing.investigation
    return None


def _prompt_utest_id(
    investigation: str,
    guess: str,
    laboratory: str,
    *,
    stdout: object,
    style: object,
) -> str:
    while True:
        if guess:
            stdout.write(f"  Best guess: {guess}")
            prompt = f"  Enter utest_id for '{investigation}' [{guess}] or 'u' for unknown: "
        else:
            stdout.write("  Best guess: (no match)")
            prompt = f"  Enter utest_id for '{investigation}' or press Enter for unknown: "

        answer = input(prompt).strip().lower()

        if answer == "u" or (not answer and not guess):
            utest_id = ""
        elif not answer and guess:
            utest_id = guess
        else:
            utest_id = answer

        conflict = _check_utest_id_conflict(utest_id, investigation, laboratory)
        if conflict:
            stdout.write(
                style.ERROR(f"  '{utest_id}' is already mapped to '{conflict}'. Try again.")
            )
            guess = ""
            continue
        return utest_id


def _resolve_utest_id(
    investigation: str,
    laboratory: str,
    known_utest_ids: set[str],
    default_mappings: dict[str, str],
    *,
    stdout: object,
    style: object,
) -> str:
    try:
        mapping = InvestigationMapping.objects.get(
            laboratory=laboratory, investigation=investigation
        )
    except InvestigationMapping.DoesNotExist:
        pass
    else:
        return mapping.utest_id

    guess = _best_guess_utest_id(investigation, known_utest_ids, default_mappings)

    stdout.write("")
    stdout.write(style.WARNING(f"  Unknown investigation: {investigation}"))

    utest_id = _prompt_utest_id(investigation, guess, laboratory, stdout=stdout, style=style)

    in_reportable = _utest_id_in_reportable(utest_id)

    if utest_id:
        tag = "" if in_reportable else " (NOT in reportable)"
        stdout.write(f"  Mapped: {investigation} -> {utest_id}{tag}")
    else:
        stdout.write(style.NOTICE(f"  Marked '{investigation}' as unknown to EDC."))

    InvestigationMapping.objects.create(
        laboratory=laboratory,
        investigation=investigation,
        utest_id=utest_id,
        in_reportable=in_reportable,
    )
    return utest_id


def _resolve_subject_identifier(
    name_id: str,
    *,
    cache: dict[str, str | None],
    stdout: object,
    style: object,
) -> str:
    if name_id in cache:
        return cache[name_id] or ""

    sid = _extract_subject_identifier(name_id)
    if RegisteredSubject.objects.filter(subject_identifier=sid).exists():
        cache[name_id] = sid
        return sid

    stdout.write(
        style.WARNING(
            f"  Subject not found for name_id={name_id} (tried subject_identifier={sid})"
        )
    )
    cache[name_id] = None
    return ""


class Command(BaseCommand):
    help = "Import lab results from a folder of PDF files."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "folder",
            type=str,
            help="Path to folder containing lab result PDF files.",
        )
        parser.add_argument(
            "--laboratory",
            dest="laboratory",
            required=True,
            help="Laboratory name (e.g. 'MNH').",
        )
        parser.add_argument(
            "--output",
            dest="output",
            default=None,
            help="Output CSV path. Defaults to lab_results.csv inside the PDF folder.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Parse and report without saving to the database.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        folder = Path(options["folder"]).expanduser()
        laboratory = options["laboratory"]
        if not folder.is_dir():
            raise CommandError(f"Not a directory: {folder}")

        pdf_count = len(list(folder.glob("*.pdf")))
        if pdf_count == 0:
            raise CommandError(f"No PDF files found in {folder}")

        parser_func = _resolve_parser(laboratory)

        tz = ZoneInfo(settings.TIME_ZONE)
        self.stdout.write(
            f"Parsing {pdf_count} PDF files from {folder} (tz={settings.TIME_ZONE}) ..."
        )
        df = parse_folder(folder, parser_func, tz=tz)

        if df.empty:
            self.stdout.write(self.style.WARNING("No results extracted."))
            return

        if options["output"]:
            output_path = Path(options["output"]).expanduser()
        else:
            output_path = folder / "lab_results.csv"
        df.to_csv(output_path, index=False)
        self.stdout.write(f"CSV saved to {output_path}")

        known_utest_ids = set(NormalData.objects.values_list("label", flat=True).distinct())
        default_mappings = getattr(settings, "EDC_LAB_DEFAULT_MAPPINGS", {}).get(
            laboratory, {}
        )

        self.stdout.write(
            f"Resolving investigation mappings for laboratory '{laboratory}' ..."
        )
        investigations = df["investigation"].unique()
        utest_map: dict[str, str] = {}
        for inv in sorted(investigations):
            utest_map[inv] = _resolve_utest_id(
                inv,
                laboratory,
                known_utest_ids,
                default_mappings,
                stdout=self.stdout,
                style=self.style,
            )

        mapped = sum(1 for v in utest_map.values() if v)
        unmapped = sum(1 for v in utest_map.values() if not v)
        self.stdout.write(f"Mappings: {mapped} mapped, {unmapped} unknown to EDC.")

        self._warn_not_in_reportable(laboratory)

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(f"Dry run: {len(df)} results parsed, not saved.")
            )
            return

        self._import_and_report(df, utest_map)

    def _warn_not_in_reportable(self, laboratory: str) -> None:
        not_in_reportable = InvestigationMapping.objects.filter(
            laboratory=laboratory,
            in_reportable=False,
        ).exclude(utest_id="")
        if not_in_reportable.exists():
            self.stdout.write(
                self.style.WARNING(
                    "The following utest_ids are NOT in reportable normal data:"
                )
            )
            for m in not_in_reportable:
                self.stdout.write(f"  {m.investigation} -> {m.utest_id}")

    def _import_and_report(
        self,
        df: pd.DataFrame,
        utest_map: dict[str, str],
    ) -> None:
        created, skipped, subject_not_found, unrecognized_units = self._save_results(
            df, utest_map
        )

        msg = f"Created {created} results from {df['source_file'].nunique()} files."
        if skipped:
            msg += f" Skipped {skipped} duplicates."
        if subject_not_found:
            msg += f" {subject_not_found} rows had no matching subject_identifier."
        self.stdout.write(self.style.SUCCESS(msg))

        if unrecognized_units:
            self.stdout.write(
                self.style.WARNING(
                    "The following units could not be converted (no matching "
                    "NormalData formula or conversion path):"
                )
            )
            for utest_id, units in sorted(unrecognized_units):
                self.stdout.write(f"  {utest_id}: {units}")

        sys.stdout.flush()

    def _save_results(
        self,
        df: pd.DataFrame,
        utest_map: dict[str, str],
    ) -> tuple[int, int, int, set[tuple[str, str]]]:
        subject_cache: dict[str, str | None] = {}
        created = 0
        skipped = 0
        subject_not_found = 0
        unrecognized_units: set[tuple[str, str]] = set()

        for _, row in df.iterrows():
            name_id = row.get("name_id", "")
            subject_identifier = _resolve_subject_identifier(
                name_id,
                cache=subject_cache,
                stdout=self.stdout,
                style=self.style,
            )
            if not subject_identifier:
                subject_not_found += 1

            unique_fields = dict(
                order_no=row.get("order_no", ""),
                result_no=row.get("result_no", ""),
                sample_no=row.get("sample_no", ""),
                investigation=row.get("investigation", ""),
                report_datetime=_to_datetime(row.get("reported_datetime")),
                name_id=name_id,
            )
            if Result.objects.filter(**unique_fields).exists():
                skipped += 1
                continue

            investigation = row.get("investigation", "")
            utest_id = utest_map.get(investigation, "")
            result_value = _to_decimal(row.get("result", ""))
            units = row.get("units", "")

            converted_value, converted_units = attempt_conversion(
                utest_id, result_value, units
            )

            if (
                utest_id
                and result_value is not None
                and units
                and converted_value is None
            ):
                normalized = normalize_units(units)
                if not NormalData.objects.filter(
                    label=utest_id, units=normalized
                ).exists():
                    unrecognized_units.add((utest_id, units))

            Result.objects.create(
                **unique_fields,
                subject_identifier=subject_identifier,
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
                specimen_collected_datetime=_to_datetime(
                    row.get("specimen_collected_datetime")
                ),
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
            created += 1
        return created, skipped, subject_not_found, unrecognized_units
