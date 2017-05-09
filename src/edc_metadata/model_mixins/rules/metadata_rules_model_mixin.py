from django.apps import apps as django_apps
from django.db import models

from ...constants import REQUISITION

from ...rules.exceptions import RuleGroupError
from ...rules.site_rule_groups import site_rule_groups


class MetadataRulesModelMixin(models.Model):

    """A model mixin that enables a visit model to run rule groups.
    """

    def run_rules_for_model(self, model, entry_status, panel_name=None):
        """Runs rules a given model for this visit and subject_identifier.
        """
        # FIXME: do these run for just the visit or for
        #        all visits?
        model = django_apps.get_model(*model.split('.'))
        options = self.metadata_query_options
        options.update({
            'model': model._meta.label_lower,
            'subject_identifier': self.subject_identifier})
        if model().metadata_category == REQUISITION:
            options.update({'panel_name': panel_name})
        # NOTE: Metadata should always exist!
        obj = model().metadata_model.objects.get(**options)
        obj.entry_status = entry_status
        obj.save()
        return obj

    def run_rules_for_app_label(self, source_model=None):
        """Runs all the rule groups for this app label.
        """
        try:
            for rule_group in site_rule_groups.registry.get(self._meta.app_label, []):
                if source_model:
                    try:
                        rule_group.run_for_source_model(self, source_model)
                    except AttributeError as e:
                        raise RuleGroupError(e)
                else:
                    try:
                        rule_group.run_all(self)
                    except AttributeError as e:
                        raise RuleGroupError(e)
        except AttributeError as e:
            raise RuleGroupError(e)

    class Meta:
        abstract = True
