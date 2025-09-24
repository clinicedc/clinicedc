from __future__ import annotations

import sys
from importlib import import_module

from django.conf import settings
from django.core.management.color import color_style
from django.utils.translation import gettext as _

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .forms_reference import FormsReference

style = color_style()


def make_forms_reference(
    app_label: str,
    admin_site_name: str,
    visit_schedule_name: str,
    title: str | None = None,
):
    module = import_module(app_label)
    admin_site = getattr(module.admin_site, admin_site_name)
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    title = title or _("%(title_app)s Forms Reference") % dict(title_app=app_label.upper())
    sys.stdout.write(
        style.MIGRATE_HEADING(f"Refreshing CRF reference document for {app_label}\n")
    )
    doc_folder = settings.BASE_DIR / "docs"
    if not doc_folder.exists():
        doc_folder.mkdir()

    forms = FormsReference(
        visit_schedules=[visit_schedule],
        admin_site=admin_site,
        title=title,
        add_per_form_timestamp=False,
    )

    path = doc_folder / f"forms_reference_{app_label}.md"
    forms.to_file(path=path, overwrite=True)

    sys.stdout.write(f"{path}\n")
    sys.stdout.write("Done.\n")
