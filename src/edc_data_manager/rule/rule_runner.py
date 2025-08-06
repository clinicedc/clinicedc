from __future__ import annotations

import sys
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from edc_metadata import KEYED, REQUIRED
from edc_metadata.metadata_inspector import MetaDataInspector
from edc_utils import get_utcnow

from ..models import QueryVisitSchedule
from .query_rule_wrapper import QueryRuleWrapper

if TYPE_CHECKING:
    from ..models import QueryRule


class RuleRunner:
    def __init__(
        self,
        query_rule_obj: QueryRule = None,
        now: datetime = None,
        verbose: bool | None = None,
    ):
        self.query_rule_obj = query_rule_obj  # query rule model instance
        self.now = now or get_utcnow()
        self.verbose = verbose

    @property
    def reference(self):
        return self.query_rule_obj.reference

    def run(self, query_rules_data: dict[str, list[QueryRuleWrapper]] | None = None):
        """Returns number of created and resolved queries after
        running all wrapped query rule objs included in
        query_rules_data.
        """
        created_counter = 0
        resolved_counter = 0
        query_rules_data = query_rules_data or self.query_rules_data
        for key, wrapped_query_rules in query_rules_data.items():
            for wrapped_query_rule in wrapped_query_rules:
                if self.verbose:
                    sys.stdout.write(f"     - running {wrapped_query_rule}\n")
                created, resolved = wrapped_query_rule.run_handler()
                if self.verbose:
                    sys.stdout.write(
                        f"       (queries created: {created}, queries resolved: {resolved})\n"
                    )
                created_counter += created
                resolved_counter += resolved
        return created_counter, resolved_counter

    def run_one(
        self,
        subject_identifier: str = None,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        visit_code: str = None,
        timepoint: Decimal = None,
    ):
        visit_schedule_obj = QueryVisitSchedule.objects.get(
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
        )
        return self.run(
            query_rules_data={
                visit_schedule_obj.visit_code: [
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=[subject_identifier],
                        visit_schedule_obj=visit_schedule_obj,
                        timepoint=timepoint,
                        now=self.now,
                    )
                ]
            }
        )

    @property
    def query_rules_data(self) -> dict[str, list[QueryRuleWrapper]]:
        """Returns a dictionary of QueryRuleWrappers format
        {visit_code: [wrappper, ...]}.

        Important: Metadata must be up-to-date
        """
        query_rules = {}
        for visit_schedule_obj in self.query_rule_obj.visit_schedule.all():
            wrapped_query_rules = []
            if self.verbose:
                sys.stdout.write(
                    f"     - query {visit_schedule_obj.visit_schedule_name}."
                    f"{visit_schedule_obj.schedule_name}.{visit_schedule_obj.visit_code}"
                    f"(timepoint {visit_schedule_obj.timepoint})\n"
                )
            metadata_inspector = MetaDataInspector(
                model_cls=self.query_rule_obj.model_cls,
                visit_schedule_name=visit_schedule_obj.visit_schedule_name,
                schedule_name=visit_schedule_obj.schedule_name,
                visit_code=visit_schedule_obj.visit_code,
                timepoint=visit_schedule_obj.timepoint,
            )
            if metadata_inspector.required:
                wrapped_query_rules.append(
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=metadata_inspector.required,
                        visit_schedule_obj=visit_schedule_obj,
                        timepoint=visit_schedule_obj.timepoint,
                        now=self.now,
                        entry_status=REQUIRED,
                        verbose=self.verbose,
                    )
                )
            if metadata_inspector.keyed:
                wrapped_query_rules.append(
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=metadata_inspector.keyed,
                        visit_schedule_obj=visit_schedule_obj,
                        timepoint=visit_schedule_obj.timepoint,
                        now=self.now,
                        entry_status=KEYED,
                        verbose=self.verbose,
                    )
                )
            if wrapped_query_rules:
                query_rules.update({visit_schedule_obj.visit_code: wrapped_query_rules})
        return query_rules
