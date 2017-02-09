import copy
import sys

from collections import OrderedDict
from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import MetadataRulesError


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class SiteRuleGroups(object):

    """ Main controller of :class:`RuleGroup` objects.
    """

    def __init__(self):
        self.registry = OrderedDict()

    def register(self, rule_group):
        """ Register Rule groups to the list for the module the rule
        groups were declared in.
        """
        if rule_group._meta.app_label not in self.registry:
            self.registry.update({rule_group._meta.app_label: []})
        for rg in self.registry.get(rule_group._meta.app_label):
            if rg.name == rule_group.name:
                raise AlreadyRegistered(
                    'The rule group {0} is already registered'.format(
                        rule_group.name))
        self.registry.get(rule_group._meta.app_label).append(rule_group)

    def get(self, app_label):
        return self.registry.get(app_label)

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
        sys.stdout.write(' * checking for {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_rule_groups.registry)
                    import_module('{}.{}'.format(app, module_name))
                except Exception as e:
                    if 'edc_metadata' in str(e) and 'metadata_rules' not in str(e):
                        raise MetadataRulesError(
                            'Failed to import {}.metadata_rules. Got \'{}\'.'.format(app, e))
                    if 'edc_rule_groups' in str(e):
                        raise MetadataRulesError(
                            'Failed to import {}.metadata_rules. '
                            'App \'edc_rule_groups\' no longer exists. Use '
                            '\'edc_metadata.rules\' instead. '
                            'Got \'{}\'.'.format(app, e))
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        site_rule_groups.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
                else:
                    sys.stdout.write(
                        '   - registered metadata rules from \'{}\'\n'.format(app))
            except ImportError as e:
                pass

site_rule_groups = SiteRuleGroups()
