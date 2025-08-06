from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import color_style

from ...update_metadata_on_schedule_change import (
    UpdateMetadataError,
    UpdateMetadataOnScheduleChange,
)

style = color_style()


class Command(BaseCommand):
    help = "Update metadata for changed visit_schedule/schedule names"
    pattern = "^[0-9a-z_]+$"
    fieldnames = ["visit_schedule_name", "schedule_name"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--field",
            dest="field",
            default=None,
            help='Field name. Either "visit_schedule_name" or "schedule_name"',
        )

        parser.add_argument(
            "--old-value",
            dest="old_value",
            default=None,
            help="Old or existing value",
        )

        parser.add_argument(
            "--new-value",
            dest="new_value",
            default=None,
            help="New value to replace the old value",
        )

        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            default=True,
            help="Do a dry run. (Default: True)",
        )

    def handle(self, *args, **options):
        dry_run = False if options.get("dry_run", "") == "False" else True

        try:
            UpdateMetadataOnScheduleChange(
                fieldname=options.get("field"),
                new_value=options.get("new_value"),
                old_value=options.get("old_value"),
                dry_run=dry_run,
            )
        except UpdateMetadataError as e:
            raise CommandError(e)
