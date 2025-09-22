from __future__ import annotations

import csv
import random
import secrets
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING

from django.contrib.sites.models import Site

from edc_randomization.site_randomizers import site_randomizers

from ..constants import ACTIVE, PLACEBO

if TYPE_CHECKING:
    from edc_randomization.models import RandomizationList


default_assignments = [ACTIVE, PLACEBO]


def make_randomization_list_for_tests(
    full_path: Path | str | None = None,
    assignments=None,
    site_names=None,
    count=None,
    first_sid=None,
    per_site=None,
) -> Path:
    first_sid = first_sid or 1
    if per_site:
        site_names = site_names * per_site
        count = len(site_names)
        gen_site_name = (x for x in site_names)
    else:
        count = count or 50
        gen_site_name = (random.choice(site_names) for i in range(0, 50))  # nosec B311

    if not full_path:
        full_path = Path(mkdtemp()) / "randomizationlist.csv"
    else:
        full_path = Path(full_path).expanduser()
    assignments = assignments or default_assignments
    with full_path.open(mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["sid", "assignment", "site_name"])
        writer.writeheader()
        n = 0
        for i in range(first_sid, count + first_sid):
            n += 1
            assignment = random.choice(assignments)  # nosec B311
            writer.writerow(dict(sid=i, assignment=assignment, site_name=next(gen_site_name)))
    return full_path


def populate_randomization_list_for_tests(
    randomizer_name=None, site_names=None, per_site=None, overwrite_site=None
):
    randomizer = site_randomizers.get(randomizer_name)
    make_randomization_list_for_tests(
        full_path=randomizer.get_randomizationlist_path(),
        site_names=site_names,
        per_site=per_site,
    )
    randomizer.import_list(overwrite=True)
    if overwrite_site:
        site = Site.objects.get_current()
        randomizer.model_cls().objects.update(site_name=site.name)


def scramble_randomization_for_test_data(
    arms: list[str],
    randomization_list_model_cls: type[RandomizationList],
):
    choices = []
    for i in range(0, 8):
        choices.append(secrets.choice(arms))
    for obj in randomization_list_model_cls.objects.all():
        obj.assigment = secrets.choice(choices)
        obj.save_base(update_fields=["assignment"])
