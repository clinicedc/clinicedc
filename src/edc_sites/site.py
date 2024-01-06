from __future__ import annotations

import dataclasses
import json
import sys
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest as BaseWSGIRequest
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule
from edc_constants.constants import OTHER
from edc_model_admin.utils import add_to_messages_once

from .auths import view_auditallsites_codename
from .exceptions import InvalidSiteError, InvalidSiteForUser
from .single_site import SingleSite
from .utils import (
    get_change_codenames,
    get_message_text,
    get_site_model_cls,
    has_profile_or_raise,
    insert_into_domain,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site

    class WSGIRequest(BaseWSGIRequest):
        site: Site


class SiteDoesNotExist(Exception):
    pass


class AlreadyRegistered(Exception):
    pass


class AlreadyRegisteredName(Exception):
    pass


class AlreadyRegisteredDomain(Exception):
    pass


class SiteNotRegistered(Exception):
    pass


class SitesCheckError(Exception):
    pass


class SitesError(Exception):
    pass


app_name: str = getattr(settings, "APP_NAME", "edc")


def get_register_default_site() -> bool:
    return getattr(settings, "EDC_SITES_REGISTER_DEFAULT", False)


def get_default_country() -> str:
    return getattr(settings, "EDC_SITES_DEFAULT_COUNTRY", "botswana")


def get_default_country_code() -> str:
    return getattr(settings, "EDC_SITES_DEFAULT_COUNTRY_CODE", "bw")


def get_default_domain() -> str:
    return getattr(settings, "EDC_SITES_DEFAULT_DOMAIN", "localhost")


def get_insert_uat_subdomain() -> str | None:
    return getattr(settings, "EDC_SITES_UAT_DOMAIN", None)


def get_autodiscover_sites():
    return getattr(settings, "EDC_SITES_AUTODISCOVER_SITES", True)


class Sites:
    uat_subdomain = "uat"
    view_auditallsites_codename = view_auditallsites_codename

    def __init__(self):
        self.loaded = False
        self._registry = {}
        if get_register_default_site():
            self.loaded = True
            site_id = int(settings.SITE_ID)
            self._registry: dict[int, SingleSite] = {
                site_id: SingleSite(
                    site_id,
                    settings.APP_NAME,
                    country=get_default_country(),
                    country_code=get_default_country_code(),
                    domain=get_default_domain(),
                    title="what a site",
                )
            }

    def __repr__(self):
        return f"{self.__class__}(loaded={self.loaded})"

    def __str__(self):
        return f"loaded={self.loaded}, registry={self._registry}"

    def initialize(self, initialize_site_model=False):
        """Initialize the registry.

        This is for tests where you are manipulating the ``sites``
        registry. If you do this after the  ``post-migrate`` signal
        is called you will also have to initialize the Site model.
        """
        if initialize_site_model:
            for obj in get_site_model_cls().objects.all():
                try:
                    obj.siteprofile.delete()
                except ObjectDoesNotExist:
                    break
            get_site_model_cls().objects.all().delete()
        self.__init__()

    def register(self, *single_sites: SingleSite):
        if not self.loaded:
            self._registry = {}
            self.loaded = True
        if "makemigrations" not in sys.argv:
            for single_site in single_sites:
                if single_site.site_id in self._registry:
                    raise AlreadyRegistered(f"Site already registered. Got `{single_site}`.")
                if single_site.name in [s.name for s in self._registry.values()]:
                    raise AlreadyRegisteredName(
                        f"Site with this name is already registered. Got `{single_site}`."
                    )
                if get_insert_uat_subdomain():
                    domain = insert_into_domain(single_site.domain, self.uat_subdomain)
                    single_site = dataclasses.replace(single_site, domain=domain)
                if single_site.domain in [s.domain for s in self._registry.values()]:
                    raise AlreadyRegisteredDomain(
                        f"Site with this domain is already registered. Got `{single_site}`."
                    )
                self._registry.update({single_site.site_id: single_site})

    def get(self, site_id: int) -> SingleSite:
        """Returns a SingleSite instance for this site_id or
        raises.

        If the reqistry is empty, check you have created a `sites.py`
        and called `register`.

        If you are just running tests, you may only need to set
        ``settings.EDC_SITES_REGISTER_DEFAULT=True``.
        """
        if site_id not in self._registry:
            site_ids = [s.site_id for s in self.all(aslist=True)]
            if not site_ids:
                msg = "In fact, no sites have been registered!"
            else:
                msg = f"Expected one of {[s.site_id for s in self.all(aslist=True)]}."
            raise SiteNotRegistered(
                f"Site not registered. {msg} See {repr(self)}. Got `{site_id}`."
            )
        return self._registry.get(site_id)

    def get_by_attr(self, attrname: str, value: Any) -> SingleSite:
        for single_site in self._registry.values():
            if getattr(single_site, attrname) == value:
                return single_site
        raise SiteDoesNotExist(f"No site exists with `{attrname}`==`{value}`.")

    def all(self, aslist: bool | None = None) -> dict[int, SingleSite] | list[SingleSite]:
        if aslist:
            return list(self._registry.values())
        return self._registry

    @property
    def countries(self) -> list[str]:
        return list(set([single_site.country for single_site in self._registry.values()]))

    def get_by_country(
        self, country: str, aslist: bool | None = None
    ) -> dict[int, SingleSite] | list[SingleSite]:
        if aslist:
            return [
                single_site
                for single_site in self.all(aslist=True)
                if single_site.country == country
            ]

        return {
            site_id: single_site
            for site_id, single_site in self._registry.items()
            if single_site.country == country
        }

    def get_site_ids_for_user(
        self,
        request: WSGIRequest | None = None,
        user: User | None = None,
        site_id: int | None = None,
    ) -> list[int]:
        """Returns a list of site ids for this user, including the
        current site.
        """
        if request:
            user = request.user
            site_id = request.site.id
        return [site_id] + self.get_view_only_site_ids_for_user(
            request=request, user=user, site_id=site_id
        )

    def get_view_only_site_ids_for_user(
        self,
        request: WSGIRequest | None = None,
        user: User | None = None,
        site_id: int | None = None,
    ) -> list[int]:
        """Returns a list of any sites the user may have view
        access to, not including the current.

        Checks for codename `edc_sites.view_auditorallsites` perms and
        confirms user does not have add/change/delete perms to any
        resources.
        """
        if request:
            user = request.user
            site_id = request.site.id

        if site_id != get_current_site(request).id:
            raise InvalidSiteError(
                f"Expected the current site. Current site is "
                f"`{get_current_site(request).id}`. "
                f"See user `{user}`. Got {site_id}."
            )
        site_id = sites.get(site_id).site_id
        has_profile_or_raise(user)
        sites.site_in_profile_or_raise(user=user, site_id=site_id)
        # now check for special view codename from user account
        site_ids = []
        if user.has_perm(f"edc_sites.{self.view_auditallsites_codename}"):
            if get_change_codenames(user):
                if request:
                    add_to_messages_once(
                        get_message_text(messages.ERROR), request, messages.ERROR
                    )
            else:
                site_ids = [s.id for s in user.userprofile.sites.all() if s.id != site_id]
                if request:
                    add_to_messages_once(
                        get_message_text(messages.WARNING), request, messages.WARNING
                    )
        return site_ids

    def user_may_view_other_sites(self, request: WSGIRequest) -> bool:
        return True if self.get_view_only_site_ids_for_user(request=request) else False

    @staticmethod
    def site_in_profile_or_raise(user: User, site_id: int) -> None:
        """Raises if user does not have site in their UserProfile."""
        try:
            user.userprofile.sites.get(id=site_id).id
        except ObjectDoesNotExist:
            raise InvalidSiteForUser(
                "User is not configured to access this site. See also UserProfile. "
                f"Got {site_id}."
            )

    def get_language_choices_tuple(
        self, site: Site | None = None, site_id: int | None = None, other=None
    ) -> tuple | None:
        """Returns a choices tuple of languages from the site object to
        be used on the `languages` modelform field.

        See also: SingleSite and SiteModelAdminMixin.
        """
        site_id = getattr(site, "id", site_id)
        single_site = self.get(site_id)
        languages = single_site.languages
        if other:
            languages.update({OTHER: "Other"})
        return tuple((k, v) for k, v in languages.items())

    @staticmethod
    def get_current_site_obj(request: WSGIRequest | None) -> Site:
        if request:
            return request.site
        return get_site_model_cls().objects.get_current()

    def get_current_site(self, request: WSGIRequest | None = None) -> SingleSite:
        if request:
            return self.get(request.site.id)
        return self.get(get_site_model_cls().objects.get_current().id)

    def get_current_country(self, request: WSGIRequest | None = None) -> str:
        single_site = self.get_current_site(request)
        return single_site.country

    def check(self):
        """Checks the Site / SiteProfile tables are in sync"""
        if not get_site_model_cls().objects.all().exists():
            raise SitesCheckError("No sites have been imported. You need to run migrate")
        ids1 = sorted(list(self.all()))
        ids2 = [
            x[0] for x in get_site_model_cls().objects.values_list("id").all().order_by("id")
        ]
        if ids1 != ids2:
            raise SitesCheckError(
                f"Site table is out of sync. Got registered sites = {ids1}. "
                f"Sites in Sites model = {ids2}. Try running migrate."
            )
        for site_id, single_site in self._registry.items():
            site_obj = get_site_model_cls().objects.get(id=site_id)
            for attr in ["name", "domain"]:
                try:
                    self.get_by_attr(attr, getattr(site_obj, attr))
                except SiteDoesNotExist as e:
                    raise SitesCheckError(f"{e}. Try running migrate.")
            for attr in ["country", "country_code"]:
                try:
                    self.get_by_attr(attr, getattr(site_obj.siteprofile, attr))
                except SiteDoesNotExist as e:
                    raise SitesCheckError(f"{e}. Try running migrate.")
            try:
                self.get_by_attr(
                    "languages", json.loads(getattr(site_obj.siteprofile, "languages"))
                )
            except SiteDoesNotExist as e:
                raise SitesCheckError(f"{e}. Try running migrate.")
            if site_obj.siteprofile.title != single_site.description:
                raise SitesCheckError(
                    f"No site exists with `title`=={site_obj.siteprofile.title}. "
                    "Try running migrate."
                )

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers query rule classes in the sites.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or "sites"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = deepcopy(sites._registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered '{module_name}' from '{app}'\n")
                except SitesError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    sites._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SitesError(str(e))
            except ImportError:
                pass


sites = Sites()
