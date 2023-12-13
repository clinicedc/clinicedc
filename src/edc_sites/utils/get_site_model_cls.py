from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


def get_site_model_cls() -> Site:
    return django_apps.get_model("sites.site")
