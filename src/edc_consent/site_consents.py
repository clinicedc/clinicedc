from __future__ import annotations

import sys
from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule
from edc_utils import floor_secs, formatted_date

from .exceptions import ConsentDefinitionDoesNotExist, ConsentDefinitionError

if TYPE_CHECKING:
    from .consent_definition import ConsentDefinition


class AlreadyRegistered(Exception):
    pass


class SiteConsentError(Exception):
    pass


class SiteConsents:
    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, cdef: ConsentDefinition) -> None:
        if cdef.name in self.registry:
            raise AlreadyRegistered(f"Consent definition already registered. Got {cdef}.")

        for version in cdef.updates_versions:
            if not self.get_consent_definition(model=cdef.model, version=version):
                raise ConsentDefinitionError(
                    f"Consent definition is configured to update a version that has "
                    f"not been registered. See {cdef}. Got {version}."
                )
        for registered_cdef in self.registry.values():
            if registered_cdef.model == cdef.model:
                if (
                    registered_cdef.start <= cdef.start <= registered_cdef.end
                    or registered_cdef.start <= cdef.end <= registered_cdef.end
                ):
                    raise ConsentDefinitionError(
                        f"Consent period overlaps with an already registered consent "
                        f"definition. See already registered consent {registered_cdef}. "
                        f"Got {cdef}."
                    )
        self.registry.update({cdef.name: cdef})
        self.loaded = True

    def get_registry_display(self):
        return "', '".join(
            [cdef.display_name for cdef in sorted(list(self.registry.values()))]
        )

    def get_consent_definition(
        self,
        model: str = None,
        report_datetime: datetime | None = None,
        version: str | None = None,
    ) -> ConsentDefinition:
        """Returns a single consent definition valid for the given criteria.

        Filters the registry by each param given.
        """
        cdefs = self.get_consent_definitions(
            model=model, report_datetime=report_datetime, version=version
        )
        if len(cdefs) > 1:
            as_string = ", ".join(list(set([cdef.name for cdef in cdefs])))
            raise SiteConsentError(f"Multiple consent definitions returned. Got {as_string}. ")
        return cdefs[0]

    def get_consent_definitions(
        self,
        model: str = None,
        report_datetime: datetime | None = None,
        version: str | None = None,
    ) -> list[ConsentDefinition]:
        """Return a list of consent definitions valid for the given
        criteria.

        Filters the registry by each param given.
        """
        # confirm loaded
        if not self.registry.values() or not self.loaded:
            raise SiteConsentError(
                "No consent definitions have been registered with `site_consents`. "
            )

        # copy registry
        cdefs: list[ConsentDefinition] = [cdef for cdef in self.registry.values()]

        # model
        if model:
            cdefs = [cdef for cdef in cdefs if model in ([cdef.model] + cdef.proxy_models)]
            if not cdefs:
                raise ConsentDefinitionDoesNotExist(
                    f"There are no consent definitions using this model. Got {model}."
                )
        # report_datetime
        if report_datetime:
            cdefs = [
                cdef
                for cdef in cdefs
                if floor_secs(cdef.start)
                <= floor_secs(report_datetime)
                <= floor_secs(cdef.end)
            ]
            if not cdefs:
                date_string = formatted_date(report_datetime)
                raise ConsentDefinitionDoesNotExist(
                    "Date does not fall within the validity period of any consent definition. "
                    f"Got {date_string}. Consent definitions are: "
                    f"{self.get_registry_display()}."
                )

        # version
        if version:
            cdefs = [cdef for cdef in cdefs if cdef.version == version]
            if not cdefs:
                raise ConsentDefinitionDoesNotExist(
                    f"There are no consent definitions for this version. Got {version}. "
                    f"Consent definitions are: {self.get_registry_display()}."
                )
        return cdefs

    @staticmethod
    def autodiscover(module_name=None, verbose=True):
        """Autodiscovers consent classes in the consents.py file of
        any INSTALLED_APP.
        """
        before_import_registry = None
        module_name = module_name or "consents"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = deepcopy(site_consents.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered consent definitions '{module_name}' from '{app}'\n")
                except SiteConsentError as e:
                    writer(f"   - loading {app}.consents ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_consents.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteConsentError(str(e))
            except ImportError:
                pass


site_consents = SiteConsents()
