import sys

from django.conf import settings

from ..models import QueryRule
from .rule_runner import RuleRunner

DATA_MANAGER_ENABLED = getattr(settings, "DATA_MANAGER_ENABLED", True)


def update_query_rules(pks=None, verbose=None):
    total_created = 0
    total_resolved = 0
    if verbose:
        sys.stdout.write("\nRunning query rules:\n")
    if not DATA_MANAGER_ENABLED:
        sys.stdout.write(
            "Disabled. To enable, set settings.DATA_MANAGER_ENABLED = True. Done\n"
        )
    else:
        opts = dict(active=True)
        if pks:
            opts.update(id__in=pks)
        query_rules = QueryRule.objects.filter(**opts)
        sys.stdout.write(
            f"  Found {query_rules.count()} rule{'s'[:query_rules.count()^1]} to run.\n"
        )
        for index, query_rule_obj in enumerate(query_rules.all()):
            if verbose:
                sys.stdout.write(f"  {index + 1}. {query_rule_obj}\n")
            rule_runner = RuleRunner(query_rule_obj, verbose=verbose)
            created, resolved = rule_runner.run()
            total_created += created
            total_resolved += resolved
        if verbose:
            sys.stdout.write(f"  total queries created {total_created}\n")
            sys.stdout.write(f"  total queries resolved {total_resolved}\n")
    sys.stdout.write("Done.\n")
    return {"created": total_created, "resolved": total_resolved}
