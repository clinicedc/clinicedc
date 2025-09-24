from __future__ import annotations

import sys
from importlib import import_module
from importlib.metadata import version
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
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
    doc_folder: str | None = None,
):
    module = import_module(app_label)
    default_doc_folder = Path(settings.BASE_DIR / "docs")
    filename = filename or f"forms_reference_{app_label}.md"
    admin_site = getattr(module.admin_site, admin_site_name)
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    title = title or _("%(title_app)s Forms Reference") % dict(title_app=app_label.upper())
    sys.stdout.write(
        style.MIGRATE_HEADING(f"Refreshing CRF reference document for {app_label}\n")
    )
    doc_folder = doc_folder or default_doc_folder
    if doc_folder == default_doc_folder and not default_doc_folder.exists():
        doc_folder.mkdir(parents=False, exist_ok=False)

    forms = FormsReference(
        visit_schedules=[visit_schedule],
        admin_site=admin_site,
        title=f"{title} v{version(settings.APP_NAME)}",
        add_per_form_timestamp=False,
    )

    path = doc_folder / filename
    forms.to_file(path=path, overwrite=True)

    sys.stdout.write(f"{path}\n")
    sys.stdout.write("Done\n")


class Command(BaseCommand):
    help = "Update forms reference document (.md)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app-label",
            dest="app_label",
            default=None,
        )

        parser.add_argument(
            "--admin-site",
            dest="admin_site_name",
            default=None,
        )

        parser.add_argument(
            "--visit-schedule",
            dest="visit_schedule_name",
            default=None,
        )

        parser.add_argument(
            "--title",
            dest="title",
            default=None,
        )

        parser.add_argument(
            "--doc_folder",
            dest="doc_folder",
            default=None,
        )

    def handle(self, *args, **options):  # noqa: ARG002
        app_label = options["app_label"]
        admin_site_name = options["admin_site_name"]
        visit_schedule_name = options["visit_schedule_name"]
        title = options["title"]
        doc_folder = options["doc_folder"]

        if not app_label or not admin_site_name or not visit_schedule_name:
            raise CommandError(f"parameter missing. got {options}")

        update_forms_reference(
            app_label=app_label,
            admin_site_name=admin_site_name,
            visit_schedule_name=visit_schedule_name,
            title=title,
            doc_folder=doc_folder,
        )
