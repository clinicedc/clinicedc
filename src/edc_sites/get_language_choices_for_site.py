from __future__ import annotations

import json

from django.apps import apps as django_apps
from edc_constants.constants import OTHER


def get_language_choices_for_site(site, other=None) -> tuple | None:
    site_profile_model_cls = django_apps.get_model("edc_sites.siteprofile")
    obj = site_profile_model_cls.objects.get(site=site)
    if obj.languages:
        languages = json.loads(obj.languages)
        if other:
            languages.update({OTHER: "Other"})
        return tuple((k, v) for k, v in languages.items())
    return None
