from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .rule import update_query_rules


@shared_task(name="update_query_rules_task")
def update_query_rules_task(pks=None):
    return update_query_rules(pks=pks)
