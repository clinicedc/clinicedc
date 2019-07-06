from edc_registration.models import RegisteredSubject

from ..site_data_manager import site_data_manager


class RuleWrapper:
    def __init__(self, query_rule=None, subject_identifiers=None, visit_schedules=None):
        self.query_rule = query_rule
        self.subject_identifiers = subject_identifiers
        if visit_schedules:
            self.visit_schedules = visit_schedules
        else:
            self.visit_schedules = self.query_rule.visit_schedule.all()

    @property
    def handler(self):
        return site_data_manager.get_rule_handler(self.query_rule.rule_handler_name)

    def run(self):
        """Create a DataQuery for each subject_identifier / visit_schedule.
        """
        created = 0
        resolved = 0
        for subject_identifier in self.subject_identifiers:
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=subject_identifier
            )
            for visit_schedule in self.visit_schedules:
                handler = self.handler(
                    rule=self,
                    registered_subject=registered_subject,
                    visit_schedule=visit_schedule,
                )
                handler.run()
                created += handler.created_counter
                resolved += handler.resolved_counter
        return created, resolved

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"model={self.query_rule.model_cls._meta.label_lower} "
            f"query_rule={self.query_rule.title})"
        )

    def __str__(self):
        return (
            f"model={self.query_rule.model_cls._meta.label_lower} "
            f"query_rule={self.query_rule.title}"
        )
