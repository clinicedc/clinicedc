from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def validated_site_id(
    all_sites, site_id: int | None = None, request: WSGIRequest = None
) -> int | None:
    site_ids = []
    for country, sites in all_sites.items():
        site_ids.extend([single_site.site_id for single_site in sites])
    if request:
        site = getattr(request, "site", None)
        site_id = getattr(site, "id", None)
    if site_id and site_id in site_ids:
        return site_id
    return None
