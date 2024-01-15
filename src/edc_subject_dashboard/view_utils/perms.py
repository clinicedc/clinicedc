from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Type

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.shortcuts import get_object_or_404
from edc_sites import site_sites

__all__ = ["Perms"]


@dataclass
class Perms:
    user: InitVar[User] = None
    model_cls: InitVar[Type[models.Model]] = None
    current_site: InitVar[Site] = None
    site: InitVar[Site] = None
    add: bool = field(default=False, init=False)
    change: bool = field(default=False, init=False)
    delete: bool = field(default=False, init=False)
    view: bool = field(default=False, init=False)

    def __post_init__(
        self, user: User, model_cls: Type[models.Model], current_site: Site, site: Site
    ):
        self.user = get_object_or_404(User, pk=user.id)

        app_label = model_cls._meta.app_label
        for action in ["add", "change", "view", "delete"]:
            codename = get_permission_codename(action, model_cls._meta)
            setattr(self, action, user.has_perm(f"{app_label}.{codename}"))

        # check site
        has_site_change_access = False
        has_site_add_access = False
        has_site_view_access = False

        site_sites.site_in_profile_or_raise(user=user, site_id=current_site.id)
        if current_site.id == site.id:
            has_site_change_access = True
            has_site_add_access = True

        view_only_sites = site_sites.get_view_only_site_ids_for_user(
            user=user, site_id=current_site.id
        )
        if site.id in view_only_sites:
            # oops, model's site is view only for user
            has_site_change_access = False
            has_site_add_access = False
            has_site_view_access = True

        if self.add and not has_site_add_access:
            self.add = False
        if self.change and not has_site_change_access:
            self.change = False
        if self.view and not has_site_view_access:
            self.view = False
