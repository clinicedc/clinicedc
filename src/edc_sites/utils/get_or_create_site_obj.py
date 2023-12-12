from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ..single_site import SiteDomainRequiredError

if TYPE_CHECKING:
    from ..single_site import SingleSite


def get_or_create_site_obj(single_site: SingleSite, apps):
    if "multisite" in settings.INSTALLED_APPS and not single_site.domain:
        raise SiteDomainRequiredError(
            f"Domain required when using `multisite`. Got None for `{single_site.name}`"
        )
    site_model_cls = apps.get_model("sites", "Site")
    try:
        site_obj = site_model_cls.objects.get(pk=single_site.site_id)
    except ObjectDoesNotExist:
        site_obj = site_model_cls.objects.create(
            pk=single_site.site_id, name=single_site.name, domain=single_site.domain
        )
    else:
        site_obj.name = single_site.name
        site_obj.domain = single_site.domain
        site_obj.save()
    return site_obj
