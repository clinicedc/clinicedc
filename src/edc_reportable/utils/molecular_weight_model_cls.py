from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from edc_reportable.models import MolecularWeight


def molecular_weight_model_cls() -> type[MolecularWeight]:
    return django_apps.get_model("edc_reportable", "MolecularWeight")
