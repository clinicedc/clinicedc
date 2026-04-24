from __future__ import annotations

import sys
from importlib.metadata import version
from pathlib import Path
from typing import IO

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.utils.translation import gettext as _

from edc_form_describer.forms_reference import FormsReference
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

style = color_style()


def update_forms_reference(
    app_label: str,
    admin_site_name: str,
    visit_schedule_name: str,
    title: str | None = None,
    filename: str | None = None,
    doc_folder: str | Path | None = None,
    stdout: IO[str] | None = None,
):
    stdout = stdout or sys.stdout
    module = apps.get_app_config(app_label).module
    default_doc_folder = Path(settings.BASE_DIR) / "docs"
    filename = filename or f"forms_reference_{app_label}.md"
    admin_site = getattr(module.admin_site, admin_site_name)
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    title = title or _("%(title_app)s Forms Reference") % dict(title_app=app_label.upper())
    stdout.write(
        style.MIGRATE_HEADING(f"Refreshing CRF reference document for {app_label}\n")
    )
    doc_folder = Path(doc_folder).expanduser() if doc_folder else default_doc_folder
    doc_folder.mkdir(parents=True, exist_ok=True)

    forms = FormsReference(
        visit_schedules=[visit_schedule],
        admin_site=admin_site,
        title=f"{title} v{version(settings.APP_NAME)}",
        add_per_form_timestamp=False,
    )

    path = doc_folder / filename
    forms.to_file(path=path, overwrite=True)

    stdout.write(f"{path}\n")
    stdout.write("Done\n")


class Command(BaseCommand):
    help = "Update forms reference document (.md)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app-label",
            dest="app_label",
            required=True,
            help="Django app label of the module that provides admin_site.",
        )
        parser.add_argument(
            "--admin-site",
            dest="admin_site_name",
            required=True,
            help="Attribute name of the admin_site on <app>.admin_site.",
        )
        parser.add_argument(
            "--visit-schedule",
            dest="visit_schedule_name",
            required=True,
            help="Registered visit-schedule name.",
        )
        parser.add_argument(
            "--title",
            dest="title",
            default=None,
            help="Optional document title. Defaults to '<APP_LABEL> Forms Reference'.",
        )
        parser.add_argument(
            "--filename",
            dest="filename",
            default=None,
            help="Output filename. Defaults to 'forms_reference_<app_label>.md'.",
        )
        parser.add_argument(
            "--doc-folder",
            dest="doc_folder",
            default=None,
            help=(
                "Output folder. Defaults to $BASE_DIR/docs. "
                "Created if it does not exist."
            ),
        )

    def handle(self, *args, **options):  # noqa: ARG002
        update_forms_reference(
            app_label=options["app_label"],
            admin_site_name=options["admin_site_name"],
            visit_schedule_name=options["visit_schedule_name"],
            title=options["title"],
            filename=options["filename"],
            doc_folder=options["doc_folder"],
            stdout=self.stdout,
        )
