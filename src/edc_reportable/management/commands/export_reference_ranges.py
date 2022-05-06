import csv
import os
import pdb
import sys
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from edc_reportable.normal_data.africa import normal_data

style = color_style()


def export_reference_ranges(path: Optional[str]):
    sys.stdout.write(style.MIGRATE_HEADING("Export reference ranges to document\n"))
    header = ["utestid"]
    full_path = os.path.join(
        os.path.expanduser(path or settings.EXPORT_FOLDER), "normal_ranges.csv"
    )
    for utestid, data in normal_data.items():
        for item in data:
            header.extend(list(item.keys()))
            break
        break
    with open(full_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        print(header)
        writer.writeheader()
        for utestid, data in normal_data.items():
            for item in data:
                item.update(utestid=utestid)
                writer.writerow(item)
    return full_path


class Command(BaseCommand):

    help = "Export reference ranges to document (.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="~/",
            action="store_true",
            dest="path",
            help="Export path/folder",
        )

    def handle(self, *args, **options):

        export_reference_ranges(path=options["path"])
