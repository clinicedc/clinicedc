import sys
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.management import color_style

from .data import molecular_weights
from .utils import load_all_reference_ranges

if TYPE_CHECKING:
    from .models import MolecularWeight

style = color_style()


def load_mw():
    model_cls: MolecularWeight = django_apps.get_model("edc_reportable", "MolecularWeight")
    for label, mw in molecular_weights.items():
        model_cls.objects.get_or_create(label=label, mw=mw)


def post_migrate_load_reference_ranges(sender=None, **kwargs):
    sys.stdout.write(style.MIGRATE_HEADING("Loading reference ranges (reportables):\n"))
    load_mw()
    load_all_reference_ranges()
