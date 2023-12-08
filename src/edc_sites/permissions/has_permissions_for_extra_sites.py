from functools import cache

from django.core.handlers.wsgi import WSGIRequest

from .site_ids_with_permissions import site_ids_with_permissions


@cache
def has_permissions_for_extra_sites(request: WSGIRequest) -> bool:
    site_ids = site_ids_with_permissions(request)
    if not site_ids or site_ids == [request.site.id]:
        return False
    return True
