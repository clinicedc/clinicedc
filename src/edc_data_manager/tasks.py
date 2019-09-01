from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from edc_data_manager.models import QueryRule
from edc_data_manager.rule import RuleRunner


DATA_MANAGER_ENABLED = getattr(settings, "DATA_MANAGER_ENABLED", True)


@shared_task(name="update_query_rules")
def update_query_rules(pks=None):
    if DATA_MANAGER_ENABLED:
        if pks:
            query_rules = QueryRule.objects.filter(id__in=pks, active=True)
        else:
            query_rules = QueryRule.objects.filter(active=True)
        total_created = 0
        total_resolved = 0
        for query_rule_obj in query_rules:
            rule_runner = RuleRunner(query_rule_obj)
            created, resolved = rule_runner.run()
            total_created += created
            total_resolved += resolved
        return {"created": total_created, "resolved": total_resolved}
    return {"created": 0, "resolved": 0}
