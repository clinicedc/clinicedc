from ..models import CrfQueryRule
from .rule_runner import RuleRunner


def update_crf_query_rules(pks=None):
    if pks:
        crf_query_rules = CrfQueryRule.objects.filter(id__in=pks, active=True)
    else:
        crf_query_rules = CrfQueryRule.objects.filter(active=True)

    total_created = 0
    total_resolved = 0
    for crf_query_rule in crf_query_rules:
        rule_runner = RuleRunner(crf_query_rule)
        created, resolved = rule_runner.run()
        total_created += created
        total_resolved += resolved
    return {"created": total_created, "resolved": total_resolved}
