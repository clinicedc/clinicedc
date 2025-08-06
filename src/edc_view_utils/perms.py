from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Type

from django.contrib.auth import get_permission_codename
from edc_sites.site import sites as site_sites

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site
    from django.db import models

__all__ = ["Perms"]


@dataclass
class SitePerms:
    """Contains add/change/delete/view perms by site.

    Query the sites in the user's profile. Also check
    if the user has additional perms to view sites
    other than the current.

    See also `get_view_only_site_ids_for_user` in edc_sites.sites.
    """

    user: InitVar[User] = None
    current_site: InitVar[Site] = None
    site: InitVar[Site] = None
    add: bool = field(default=False, init=False)
    change: bool = field(default=False, init=False)
    delete: bool = field(default=False, init=False)
    view: bool = field(default=False, init=False)

    def __post_init__(self, user: User, current_site: Site, site: Site) -> None:
        site_sites.site_in_profile_or_raise(user=user, site_id=current_site.id)
        if current_site.id == site.id:
            self.change = True
            self.add = True
            self.view = True
        view_only_sites = site_sites.get_view_only_site_ids_for_user(
            user=user, site_id=current_site.id
        )
        if site.id in view_only_sites:
            # oops, model's site is view only for user
            self.change = False
            self.add = False
            self.view = True


@dataclass
class Perms:
    """Contains model class perms (add/change/delete/view/view_only)
    for this user.

    Here we consider model class, the current site, the sites in
    user's profile, and userprofile.is_multisite_viewer.
    """

    user: User = None
    model_cls: InitVar[Type[models.Model]] = None
    current_site: Site = None
    site: Site = None
    add: bool = field(default=False, init=False)
    change: bool = field(default=False, init=False)
    delete: bool = field(default=False, init=False)
    view: bool = field(default=False, init=False)
    view_only: bool = field(default=False, init=False)
    _site_perms: SitePerms = field(default=None, init=False)

    def __post_init__(self, model_cls: Type[models.Model]):
        # self.user = get_object_or_404(User, pk=self.user.id)
        # set add, change, delete, view attrs for this user
        # based on the model class
        app_label = model_cls._meta.app_label
        for action in ["add", "change", "view", "delete"]:
            codename = get_permission_codename(action, model_cls._meta)
            setattr(self, action, self.user.has_perm(f"{app_label}.{codename}"))
        # combine the above with permissions relative to the site
        if self.add and not self.site_perms.add:
            self.add = False
        if self.change and not self.site_perms.change:
            self.change = False
        if self.view and not self.site_perms.view:
            self.view = False
        self.view_only = not self.add and not self.change and self.view

    @property
    def site_perms(self) -> SitePerms:
        if not self._site_perms:
            self._site_perms = SitePerms(
                user=self.user,
                current_site=self.current_site,
                site=self.site,
            )
        return self._site_perms
