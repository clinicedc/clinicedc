import sys

from copy import deepcopy
from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule
from edc_utils import convert_php_dateformat

from .exceptions import ConsentObjectDoesNotExist
from .consent_object_validator import ConsentObjectValidator


class ConsentError(Exception):
    pass


class AlreadyRegistered(Exception):
    pass


class SiteConsentError(Exception):
    pass


class SiteConsents:
    validate_consent_object = ConsentObjectValidator

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, consent=None):
        """Register consent `objects`, not models."""
        if consent.name in self.registry:
            raise AlreadyRegistered(
                f"Consent object already registered. Got {consent}."
            )
        self.validate_consent_object(consent=consent, consents=self.consents)
        self.registry.update({consent.name: consent})
        self.loaded = True

    @property
    def consents(self):
        """Returns an ordered list of consent objects.
        """
        consents = list(self.registry.values())
        return sorted(consents, key=lambda x: x.name, reverse=False)

    def get_consents_by_model(self, model=None):
        """Returns a list of consents for the given
        consent model label_lower.
        """
        return [consent for consent in self.consents if consent.model == model]

    def get_consent_for_period(
        self, model=None, report_datetime=None, consent_group=None
    ):
        """Returns a consent object with a date range that the
        given report_datetime falls within.
        """
        if not self.consents or not self.loaded:
            raise SiteConsentError(
                f"No consent objects have been registered by site consents. "
                f"Got {self.consents}, loaded={self.loaded}."
            )
        app_config = django_apps.get_app_config("edc_consent")
        consent_group = consent_group or app_config.default_consent_group
        registered_consents = self.registry.values()
        registered_consents = [
            c
            for c in registered_consents
            if c.group == consent_group and c.model == model
        ]
        if not registered_consents:
            raise SiteConsentError(
                f"No matching registered consent object in site consents. "
                f"Got consent_model={model}, consent_group={consent_group}, "
                f"report_datetime={report_datetime}. ",
                f"Expected one of {self.consents}.",
            )
        registered_consents = [
            c for c in registered_consents if c.start <= report_datetime <= c.end
        ]
        if not registered_consents:
            raise SiteConsentError(
                f"Date does not fall within the period of any registered consent "
                f"object. Got {report_datetime}. Expected one of {self.consents}."
            )
        return registered_consents[0]

    def get_consent(
        self,
        model=None,
        report_datetime=None,
        version=None,
        consent_group=None,
        **kwargs,
    ):
        """Return consent object, not model, valid for the datetime.
        """
        app_config = django_apps.get_app_config("edc_consent")
        consent_group = consent_group or app_config.default_consent_group
        registered_consents = self.registry.values()
        if consent_group:
            registered_consents = [
                c for c in registered_consents if c.group == consent_group
            ]
        if not registered_consents:
            raise ConsentObjectDoesNotExist(
                f"No matching consent in site consents. "
                f"Got consent_group={consent_group}."
            )
        if version:
            registered_consents = [
                c for c in registered_consents if c.version == version
            ]
        if not registered_consents:
            raise ConsentObjectDoesNotExist(
                f"No matching consent in site consents. "
                f"Got consent_group={consent_group}, version={version}."
            )
        if model:
            registered_consents = [c for c in registered_consents if c.model == model]
        if not registered_consents:
            raise ConsentObjectDoesNotExist(
                f"No matching consent in site consents. "
                f"Got consent_group={consent_group}, version={version}, "
                f"model={model}."
            )
        registered_consents = [
            c for c in registered_consents if c.start <= report_datetime <= c.end
        ]
        if not registered_consents:
            raise ConsentObjectDoesNotExist(
                f"No matching consent in site consents. "
                f"Got consent_group={consent_group}, version={version}, "
                f"model={model}, report_datetime={report_datetime}."
            )
        elif len(registered_consents) > 1:
            consents = list(set([c.name for c in registered_consents]))
            formatted_report_datetime = report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise ConsentError(
                f"Multiple consents found, using consent model={model}, "
                f"date={formatted_report_datetime}, "
                f"consent_group={consent_group}, version={version}. "
                f"Got {consents}"
            )
        return registered_consents[0]

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers consent classes in the consents.py file of
        any INSTALLED_APP.
        """
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
                    writer(f" * registered consents '{module_name}' from '{app}'\n")
                except ConsentError as e:
                    writer(f"   - loading {app}.consents ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_consents.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteConsentError(str(e))
            except ImportError:
                pass


site_consents = SiteConsents()
