import copy
import sys

from collections import OrderedDict
from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class SiteMetadataRulesAlreadyRegistered(Exception):
    pass


class SiteMetadataNoRulesError(Exception):
    pass


class SiteMetadataRulesImportError(Exception):
    pass


class SiteMetadataRules:

    """ Main controller of :class:`MetadataRules` objects.
    """

    def __init__(self):
        self.registry = OrderedDict()

    def register(self, rule_group_cls=None):
        """ Register MetadataRules to a list per app_label
        for the module the rule groups were declared in.
        """
        if rule_group_cls:
            if not rule_group_cls._meta.rules:
                raise SiteMetadataNoRulesError(
                    f'The metadata rule group {rule_group_cls.name} '
                    f'has no rule!')

            if rule_group_cls._meta.app_label not in self.registry:
                self.registry.update({rule_group_cls._meta.app_label: []})

            for rgroup in self.registry.get(rule_group_cls._meta.app_label):
                if rgroup.name == rule_group_cls.name:
                    raise SiteMetadataRulesAlreadyRegistered(
                        f'The metadata rule group {rule_group_cls.name} '
                        f'is already registered')
            self.registry.get(rule_group_cls._meta.app_label).append(
                rule_group_cls)

    @property
    def rule_groups(self):
        return self.registry

    def get_rule_group(self, name):
        app_label, _ = name.split('.')
        for rule_group in self.registry.get(app_label):
            if rule_group.name == name:
                return rule_group
        return None

    def update_all(self, visit_model_instance):
        """Given a visit model instance, run all rules in each rule group
        for the app_label of the visit model.
        """
        app_label = visit_model_instance._meta.app_label
        for rule_group in self.registry.get(app_label):
            for rule in rule_group.rules:
                rule.run(visit_model_instance)

    def update_for_visit_definition(self, visit_instance):
        """Given a visit model instance, run all rules in the rule group
        module for the visit definition in order of the entries
        (rule source model).
        """
        CrfEntry = django_apps.get_model('edc_metadata', 'CrfEntry')
        crf_entries = (
            CrfEntry.objects.filter(
                visit_definition__code=visit_instance.appointment.visit_definition.code)
            .order_by('entry_order'))
        for entry in crf_entries:
            source_model = entry.get_model()
            for rule in self.get_rules_for_source_model(
                    source_model, visit_instance._meta.app_label):
                rule.run(visit_instance)

    def update_rules_for_source_model(self, source_model, visit_instance):
        """Runs all rules that have a reference to the given
        source model (rule.source_model).
        """
        for rule in self.get_rules_for_source_model(
                source_model, visit_instance._meta.app_label):
            rule.run(visit_instance)

    def update_rules_for_source_fk_model(self, source_fk_model, visit_instance):
        """Runs all rules that have a reference to the given source
        FK model (rule.source_fk_model).
        """
        for rule in self.get_rules_for_source_fk_model(
                source_fk_model, visit_instance._meta.app_label):
            rule.run(visit_instance)

    def get_rules_for_source_model(self, source_model, app_label):
        """Returns a list of rules for the given source_model.
        """
        rules = []
        for rule_group in self.registry.get(app_label):
            for rule in rule_group.rules:
                if rule.source_model == source_model:
                    if rule.runif:
                        rules.append(rule)
        return rules

    def get_rules_for_registered_subject(self, app_label):
        """Returns a list of rules for the given source_fk_model.
        """
        rules = []
        for rule_group in self.registry.get(app_label):
            for rule in rule_group.rules:
                if rule.source_model._meta.object_name.lower() == 'registeredsubject':
                    rules.append(rule)
        return rules

    def get_rules_for_source_fk_model(self, source_fk_model, app_label):
        """Returns a list of rules for the given source_fk_model.
        """
        rules = []
        for rule_group in self.registry.get(app_label):
            for rule in rule_group.rules:
                if rule.source_fk_model == source_fk_model:
                    rules.append(rule)
        return rules

    def autodiscover(self, module_name=None):
        """Autodiscovers rules in the metadata_rules.py file
        of any INSTALLED_APP.
        """
        module_name = module_name or 'metadata_rules'
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_metadata_rules.registry)
                    import_module(f'{app}.{module_name}')
                except Exception as e:
                    if 'edc_metadata' in str(e) and 'metadata_rules' not in str(e):
                        raise SiteMetadataRulesImportError(
                            f'Failed to import {app}.metadata_rules. Got \'{e}\'.')
                    if 'edc_rule_groups' in str(e):
                        raise SiteMetadataRulesImportError(
                            f'Failed to import {app}.metadata_rules. '
                            f'App \'edc_rule_groups\' no longer exists. Use '
                            f'\'edc_metadata.rules\' instead. '
                            f'Got \'{e}\'.')
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_metadata_rules.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
                else:
                    sys.stdout.write(
                        f'   - registered metadata rules from \'{app}\'\n')
            except ImportError as e:
                pass


site_metadata_rules = SiteMetadataRules()
