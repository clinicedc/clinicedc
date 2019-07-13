from ..models import QueryRule
from .rule_runner import RuleRunner


def update_query_rules(pks=None):
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
