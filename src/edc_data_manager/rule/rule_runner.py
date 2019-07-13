import arrow

from edc_metadata.metadata_inspector import MetaDataInspector

from ..models import QueryVisitSchedule
from .query_rule_wrapper import QueryRuleWrapper


class RuleRunner:
    def __init__(self, query_rule_obj=None, now=None):
        self.query_rule_obj = query_rule_obj  # query rule model instance
        self.now = now or arrow.utcnow().datetime

    @property
    def reference(self):
        return self.query_rule_obj.reference

    def run(self, query_rules=None):
        """Runs all wrapped query rules included in the
        query_rules dictionary.
        """
        created_counter = 0
        resolved_counter = 0
        query_rules = query_rules or self.query_rules
        for _, wrapped_query_rules in query_rules.items():
            for wrapped_query_rule in wrapped_query_rules:
                created, resolved = wrapped_query_rule.run_handler()
                created_counter += created
                resolved_counter += resolved
        return created_counter, resolved_counter

    def run_one(
        self,
        subject_identifier=None,
        visit_schedule_name=None,
        schedule_name=None,
        visit_code=None,
        timepoint=None,
    ):
        visit_schedule = QueryVisitSchedule.objects.get(
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            timepoint=timepoint,
        )
        return self.run(
            {
                visit_schedule.visit_code: [
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=[subject_identifier],
                        visit_schedules=[visit_schedule],
                        now=self.now,
                    )
                ]
            }
        )

    @property
    def query_rules(self):
        """Returns a dictionary of QueryRuleWrappers format
        {visit_code: [wrappper, ...]}.
        """
        query_rules = {}
        for obj in self.query_rule_obj.visit_schedule.all():
            wrapped_query_rules = []
            metadata_inspector = MetaDataInspector(
                model_cls=self.query_rule_obj.model_cls,
                visit_schedule_name=obj.visit_schedule_name,
                schedule_name=obj.schedule_name,
                visit_code=obj.visit_code,
                timepoint=obj.timepoint,
            )
            if metadata_inspector.required:
                wrapped_query_rules.append(
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=metadata_inspector.required,
                        visit_schedules=[obj],
                        now=self.now,
                    )
                )
            if metadata_inspector.keyed:
                wrapped_query_rules.append(
                    QueryRuleWrapper(
                        query_rule_obj=self.query_rule_obj,
                        subject_identifiers=metadata_inspector.keyed,
                        visit_schedules=[obj],
                        now=self.now,
                    )
                )
            if wrapped_query_rules:
                query_rules.update({obj.visit_code: wrapped_query_rules})
        return query_rules
