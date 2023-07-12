import copy
import sys
from typing import Any, Optional

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class SiteMetadataRulesAlreadyRegistered(Exception):
    pass


class SiteMetadataNoRulesError(Exception):
    pass


class SiteMetadataRules:

    """Main controller of :class:`MetadataRules` objects."""

    def __init__(self) -> None:
        self.registry = {}

    def register(self, rule_group_cls: Optional[Any] = None) -> None:
        """Register MetadataRules to a list per app_label
        for the module the rule groups were declared in.
        """
        if rule_group_cls:
            if not rule_group_cls._meta.options.get("rules"):
                raise SiteMetadataNoRulesError(
                    f"The metadata rule group {rule_group_cls.name} " f"has no rule!"
                )

            if rule_group_cls._meta.app_label not in self.registry:
                self.registry.update({rule_group_cls._meta.app_label: []})

            for rgroup in self.registry.get(rule_group_cls._meta.app_label):
                if rgroup.name == rule_group_cls.name:
                    raise SiteMetadataRulesAlreadyRegistered(
                        f"The metadata rule group {rule_group_cls.name} "
                        f"is already registered"
                    )
            self.registry.get(rule_group_cls._meta.app_label).append(rule_group_cls)

    @property
    def rule_groups(self) -> Any:
        return self.registry

    def validate(self) -> None:
        for rule_groups in self.registry.values():
            for rule_group in rule_groups:
                sys.stdout.write(f"{repr(rule_group)}\n")
                rule_group.validate()

    @staticmethod
    def autodiscover(module_name: Optional[str] = None) -> None:
        """Autodiscovers rules in the metadata_rules.py file
        of any INSTALLED_APP.
        """
        module_name = module_name or "metadata_rules"
        sys.stdout.write(f" * checking for {module_name} ...\n")
        for app in django_apps.app_configs:
            try:
                before_import_registry = None
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_metadata_rules.registry)
                    import_module(f"{app}.{module_name}")
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        site_metadata_rules.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise

                else:
                    sys.stdout.write(
                        f"   - imported metadata rules from '{app}.{module_name}'\n"
                    )
            except ImportError:
                pass


site_metadata_rules = SiteMetadataRules()
