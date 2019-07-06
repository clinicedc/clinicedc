from edc_metadata.metadata_inspector import MetaDataInspector

from ..models import QueryVisitSchedule
from .rule_wrapper import RuleWrapper


class RuleRunner:
    def __init__(self, query_rule=None):
        self.query_rule = query_rule  # query rule model instance
        self.model_cls = self.query_rule.model_cls

    @property
    def reference(self):
        return self.query_rule.reference

    def run(self, rules=None):
        """Runs each rule
        """
        created_counter = 0
        resolved_counter = 0
        rules = rules or self.rules
        for _, visit_rules in rules.items():
            for visit_rule in visit_rules:
                created, resolved = visit_rule.run()
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
                    RuleWrapper(
                        query_rule=self.query_rule,
                        subject_identifiers=[subject_identifier],
                        visit_schedules=[visit_schedule],
                    )
                ]
            }
        )

    @property
    def rules(self):
        rules = {}
        for visit_schedule in self.query_rule.visit_schedule.all():
            visit_rules = []
            metadata_inspector = MetaDataInspector(
                model_cls=self.query_rule.model_cls, visit_schedule=visit_schedule
            )
            if metadata_inspector.required:
                visit_rules.append(
                    RuleWrapper(
                        query_rule=self.query_rule,
                        subject_identifiers=metadata_inspector.required,
                        visit_schedules=[visit_schedule],
                    )
                )
            if metadata_inspector.keyed:
                visit_rules.append(
                    RuleWrapper(
                        query_rule=self.query_rule,
                        subject_identifiers=metadata_inspector.keyed,
                        visit_schedules=[visit_schedule],
                    )
                )
            if visit_rules:
                rules.update({visit_schedule.visit_code: visit_rules})
        return rules
