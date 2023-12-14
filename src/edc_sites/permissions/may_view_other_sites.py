from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest

from .get_view_only_sites_for_user import get_view_only_sites_for_user


def may_view_other_sites(request: WSGIRequest) -> bool:
    """Returns True if there are view only sites (other than current)
    in the user's UserProfile.

    Use `get_view_only_sites_for_user` if you want the actual list.
    """
    return (
        True
        if get_view_only_sites_for_user(request.user, request.site.id, request=request)
        else False
    )
