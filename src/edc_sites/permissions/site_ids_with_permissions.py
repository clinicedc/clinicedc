from functools import cache

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _
from edc_auth.auth_objects import ACCOUNT_MANAGER_ROLE
from edc_auth.utils import get_codenames_for_role
from edc_model_admin.utils import add_to_messages_once

from edc_sites.auths import codename


class InvalidSiteForUser(Exception):
    pass


successmsg = _(
    "You have permissions to view data from multiple sites. "
    "The data showing may not be from the current site"
)
warnmsg = _(
    "Showing data from the current site only. Although you have permissions to view "
    "data from multiple sites you also have permissions to add, change or delete data. "
    "This is not permitted when viewing data from multiple sites."
)


@cache
def site_ids_with_permissions(request: WSGIRequest) -> list[int]:
    """Returns a list with extra site ids if user has
    `edc_sites.view_auditorallsites` perms and no add/change/delete perms.
    """
    site_ids = []
    if userprofile := getattr(request.user, "userprofile", None):
        try:
            site_ids = [userprofile.sites.get(id=request.site.id).id]
        except ObjectDoesNotExist:
            sites = [str(obj.id) for obj in userprofile.sites.all()] or ["None"]
            raise InvalidSiteForUser(
                "User is not configured to access this site. See also UserProfile. "
                f"Expected one of [{','.join(sites)}]. Got {request.site.id}."
            )
    if request.user.has_perm(f"edc_sites.{codename}"):
        perms = [
            perm.codename
            for perm in request.user.user_permissions.all()
            if perm.codename not in get_codenames_for_role(ACCOUNT_MANAGER_ROLE)
        ]
        if perms and not [c for c in perms if "add" in c or "change" in c or "delete" in c]:
            site_ids = [obj.id for obj in request.user.userprofile.sites.all()]
            site_ids.sort()
            add_to_messages_once(successmsg, request, messages.INFO)
        else:
            add_to_messages_once(warnmsg, request, messages.WARNING)
    return site_ids or [request.site.id]
