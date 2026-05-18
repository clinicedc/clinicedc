"""Update an investigation mapping and backfill Result rows.

Usage::

    manage.py update_mapping --laboratory "MNH" \
        --investigation "ABS NEUTROPHIL" --utest-id "neutrophil"
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from edc_lab_results.models import InvestigationMapping, Result
from edc_reportable.models import NormalData


class Command(BaseCommand):
    help = (
        "Update an investigation mapping and backfill "
        "utest_id on existing Result rows."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--laboratory",
            dest="laboratory",
            required=True,
            help="Laboratory name (e.g. 'MNH').",
        )
        parser.add_argument(
            "--investigation",
            dest="investigation",
            required=True,
            help="Investigation name as it appears on the PDF.",
        )
        parser.add_argument(
            "--utest-id",
            dest="utest_id",
            required=True,
            help=(
                "New utest_id value. "
                "Use empty string to mark as unknown."
            ),
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        laboratory = options["laboratory"]
        investigation = options["investigation"]
        new_utest_id = options["utest_id"].strip().lower()

        try:
            mapping = InvestigationMapping.objects.get(
                laboratory=laboratory,
                investigation=investigation,
            )
        except InvestigationMapping.DoesNotExist as e:
            raise CommandError(
                f"No mapping found for laboratory='{laboratory}', "
                f"investigation='{investigation}'."
            ) from e

        old_utest_id = mapping.utest_id

        if old_utest_id == new_utest_id:
            self.stdout.write(
                f"Already mapped: {investigation} -> "
                f"{new_utest_id!r}. Nothing to do."
            )
            return

        conflict = InvestigationMapping.objects.filter(
            laboratory=laboratory,
            utest_id=new_utest_id,
        ).exclude(pk=mapping.pk)
        if new_utest_id and conflict.exists():
            other = conflict.first()
            raise CommandError(
                f"'{new_utest_id}' is already mapped to "
                f"'{other.investigation}' for laboratory "
                f"'{laboratory}'."
            )

        in_reportable = (
            NormalData.objects.filter(label=new_utest_id).exists()
            if new_utest_id
            else False
        )

        mapping.utest_id = new_utest_id
        mapping.in_reportable = in_reportable
        mapping.save()

        tag = "" if in_reportable else " (NOT in reportable)"
        self.stdout.write(
            f"Updated mapping: {investigation} -> "
            f"{old_utest_id!r} => {new_utest_id!r}{tag}"
        )

        updated = Result.objects.filter(
            investigation=investigation,
        ).update(utest_id=new_utest_id)

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfilled {updated} Result rows."
            )
        )
