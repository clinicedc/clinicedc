from __future__ import annotations

import sys
from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule
from django.utils.translation import gettext as _
from edc_utils import floor_secs, formatted_date

from .consent_definition_validator import ConsentDefinitionValidator
from .exceptions import ConsentDefinitionDoesNotExist

if TYPE_CHECKING:
    from .consent_definition import ConsentDefinition


class AlreadyRegistered(Exception):
    pass


class SiteConsentError(Exception):
    pass


class SiteConsents:
    validate_consent_definition = ConsentDefinitionValidator

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, consent_definition: ConsentDefinition) -> None:
        if consent_definition.name in self.registry:
            raise AlreadyRegistered(
                f"Consent object already registered. Got {consent_definition}."
            )
        self.validate_consent_definition(
            consent_definition=consent_definition,
            consent_definitions=self.consent_definitions,
        )
        self.registry.update({consent_definition.name: consent_definition})
        self.loaded = True

    @property
    def consent_definitions(self) -> list[ConsentDefinition]:
        """Returns an ordered list of ConsentDefinitions"""
        return sorted(list(self.registry.values()))

    def get_consent_definitions_by_model(
        self, model: str = None
    ) -> list[ConsentDefinition] | list[str]:
        """Returns a list of consents for the given consent model
        label_lower.
        """
        consents = []
        for consent in self.consent_definitions:
            if model in ([consent.model] + consent.proxy_models):
                consents.append(consent)
        return consents

    def get_consent_definition_for_period(
        self,
        model: str = None,
        report_datetime: datetime = None,
    ) -> ConsentDefinition:
        """Returns a ConsentDefinition with a date range that the
        given report_datetime falls within.
        """
        if not self.consent_definitions or not self.loaded:
            raise SiteConsentError(
                f"No consent objects have been registered with `site_consents`. "
                f"Got {self.consent_definitions}, loaded={self.loaded}."
            )
        consent_definitions: list[ConsentDefinition] = []
        for consent_definition in self.consent_definitions_for_model_or_raise(model=model):
            if consent_definition.start <= report_datetime <= consent_definition.end:
                consent_definitions.append(consent_definition)
        if not consent_definitions:
            date_string = formatted_date(report_datetime)
            possible = "', '".join([c.display_name for c in self.consent_definitions])
            raise ConsentDefinitionDoesNotExist(
                "Consent definition not found. Date does not fall within the validity "
                f"period of any consent definition. Got {date_string}. "
                f"Possible definitions are: '{possible}'."
            )
        return consent_definitions[0]

    def get_consent_definition(
        self,
        consent_model: str = None,
        report_datetime: datetime = None,
        version=None,
    ) -> ConsentDefinition:
        """Return consent object, not model, valid for the datetime."""
        definitions: list[ConsentDefinition] = list(self.registry.values())
        if version:
            definitions = [cdef for cdef in definitions if cdef.version == version]
            if not definitions:
                raise ConsentDefinitionDoesNotExist(
                    f"Version does not match any consent definitions. Got version={version}."
                )
        definitions = [
            cdef for cdef in definitions if consent_model in ([cdef.model] + cdef.proxy_models)
        ]
        if not definitions:
            raise ConsentDefinitionDoesNotExist(
                f"No consent definitions using this model. Got model={consent_model}."
            )
        definitions = [
            cdef
            for cdef in definitions
            if floor_secs(cdef.start) <= floor_secs(report_datetime) <= floor_secs(cdef.end)
        ]
        if not definitions:
            date_string = formatted_date(report_datetime)
            possible = "', '".join([cdef.display_name for cdef in self.consent_definitions])

            raise ConsentDefinitionDoesNotExist(
                "Date does not fall within the validity period of any consent definition. "
                f"Got {date_string}. Consent definitions are: {possible}."
            )
        elif len(definitions) > 1:
            as_string = ", ".join(list(set([cdef.name for cdef in definitions])))
            raise SiteConsentError(f"Multiple consent definitions returned. Got {as_string}.")
        return definitions[0]

    def consent_definitions_for_model_or_raise(
        self, model: str = None
    ) -> list[ConsentDefinition]:
        """Returns a list of consent definitions"""
        consent_definitions = []
        for cdef in self.registry.values():
            if model in ([cdef.model] + cdef.proxy_models):
                consent_definitions.append(cdef)
        if not consent_definitions:
            possible_consents = "', '".join(
                [cdef.display_name for cdef in self.consent_definitions]
            )
            raise ConsentDefinitionDoesNotExist(
                _(
                    (
                        "Consent definition not found using this model. "
                        "Got consent_model=%(model)s, "
                        "Possible consents are: %(possible_consents)s."
                    )
                    % dict(
                        model=model,
                        possible_consents=possible_consents,
                    )
                )
            )
        return consent_definitions

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
