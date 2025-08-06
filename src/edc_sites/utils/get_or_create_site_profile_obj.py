from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from ..models import SiteProfile


def get_or_create_site_profile_obj(single_site, site_obj, apps) -> SiteProfile | None:
    site_profile_model_cls = apps.get_model("edc_sites", "SiteProfile")
    opts = dict(
        title=single_site.description,
        country=single_site.country,
        country_code=single_site.country_code,
        languages=json.dumps(single_site.languages) if single_site.languages else None,
    )
    try:
        site_profile = site_profile_model_cls.objects.get(site=site_obj)
    except ObjectDoesNotExist:
        site_profile = site_profile_model_cls.objects.create(site=site_obj, **opts)
    else:
        for k, v in opts.items():
            setattr(site_profile, k, v)
        site_profile.save()
    return site_profile
