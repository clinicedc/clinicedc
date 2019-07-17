from django.conf import settings

from ..models import QueryRule
from .rule_runner import RuleRunner

DATA_MANAGER_ENABLED = getattr(settings, "DATA_MANAGER_ENABLED", True)


def update_query_rules(pks=None):
    if DATA_MANAGER_ENABLED:
        if pks:
            query_rules = QueryRule.objects.filter(id__in=pks, active=True)
        else:
            query_rules = QueryRule.objects.filter(active=True)
        total_created = 0
        total_resolved = 0
        for query_rule in query_rules:
            rule_runner = RuleRunner(query_rule)
            created, resolved = rule_runner.run()
            total_created += created
            total_resolved += resolved
        return {"created": total_created, "resolved": total_resolved}
    return {"created": 0, "resolved": 0}
