from __future__ import annotations

import os
import sys
from importlib import import_module

from django.conf import settings
from django.core.management.color import color_style
from django.utils.translation import gettext as _
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_form_describer.forms_reference import FormsReference

style = color_style()


def make_forms_reference(
    app_label: str = None,
    admin_site_name: str = None,
    visit_schedule_name: str = None,
    title: str = None,
    path: str | None = None,
):
    module = import_module(app_label)
    admin_site = getattr(getattr(module, "admin_site"), admin_site_name)
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    title = title or _("%(title_app)s Forms Reference") % dict(title_app=app_label.upper())
    sys.stdout.write(
        style.MIGRATE_HEADING(f"Refreshing CRF reference document for {app_label}\n")
    )
    doc_folder = os.path.join(settings.BASE_DIR, "docs")
    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    forms = FormsReference(
        visit_schedules=[visit_schedule],
        admin_site=admin_site,
        title=title,
        add_per_form_timestamp=False,
    )

    path = os.path.join(doc_folder, "forms_reference.md")
    forms.to_file(path=path, overwrite=True)

    print(path)
    print("Done.")
