from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _
from edc_model_admin.utils import add_to_messages_once

from ..auths import codename
from ..exceptions import InvalidSiteError
from ..site import sites
from .utils import get_change_codenames, has_profile_or_raise

if TYPE_CHECKING:
    from django.contrib.auth.models import User


successmsg = _(
    "You have permissions to view data from multiple sites. "
    "The data showing may not be from the current site"
)
warnmsg = _(
    "Showing data from the current site only. Although you have permissions to view "
    "data from multiple sites you also have permissions to add, change or delete data. "
    "This is not permitted when viewing data from multiple sites."
)


def get_view_only_sites_for_user(
    user: User = None, site_id: int = None, request: WSGIRequest | None = None
) -> list[int]:
    """Returns a list of any sites the user may have view
    access to, not including the current.

    Checks for codename `edc_sites.view_auditorallsites` perms and
    confirms user does not have add/change/delete perms to any
    resources.
    """
    # is this the current site?
    if site_id != get_current_site(request).id:
        raise InvalidSiteError(
            f"Expected the current site. Current site is {get_current_site(request).id}. "
            f"Got {site_id}."
        )

    # is the site registered? most likely. If not, raises SiteNotRegistered.
    site_id = sites.get(site_id).site_id

    has_profile_or_raise(user)

    sites.site_in_profile_or_raise(user, site_id)

    # now check for special view codename from user account
    site_ids = []
    if user.has_perm(f"edc_sites.{codename}"):
        if get_change_codenames(user):
            if request:
                add_to_messages_once(warnmsg, request, messages.WARNING)
        else:
            site_ids = [s for s in sites.get_site_ids_for_user(user) if s != site_id]
            if request:
                add_to_messages_once(successmsg, request, messages.INFO)
    return site_ids
