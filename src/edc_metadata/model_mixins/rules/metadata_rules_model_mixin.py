from django.db import models

from ...rules import site_metadata_rules


class MetadataRulesModelError(Exception):
    pass


class MetadataRulesModelMixin(models.Model):

    """A model mixin that enables a visit model to run rule groups.
    """

    def run_metadata_rules(self):
        """Runs all the rule groups for this app label.

        Gets called in the signal.
        """
        for rule_group in site_metadata_rules.registry.get(self._meta.app_label, []):
            rule_group.evaluate_rules(visit=self)

    class Meta:
        abstract = True
