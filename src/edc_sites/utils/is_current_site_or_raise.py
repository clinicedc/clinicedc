from django.contrib.sites.shortcuts import get_current_site
from django.core.handlers.wsgi import WSGIRequest

from ..exceptions import InvalidSiteError


def is_current_site_or_raise(site_id: int, request: WSGIRequest = None) -> bool:
    if site_id != get_current_site(request).id:
        raise InvalidSiteError(
            f"Expected the current site. Current site is {get_current_site(request).id}. "
            f"Got {site_id}."
        )
    return True
