from edc_registration.models import RegisteredSubject

from ..site_data_manager import site_data_manager


class QueryRuleWrapper:
    def __init__(
        self,
        query_rule_obj=None,
        subject_identifiers=None,
        visit_schedule_obj=None,
        timepoint=None,
        visit_code_sequence=None,
        now=None,
    ):
        self.now = now
        self.query_rule_obj = query_rule_obj
        self.subject_identifiers = subject_identifiers
        self.visit_schedule_obj = visit_schedule_obj
        self.timepoint = timepoint
        self.visit_code_sequence = (
            visit_code_sequence or str(self.timepoint).split(".")[1] or 0
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"model={self.query_rule_obj.model_cls._meta.label_lower}, "
            f"query_rule={self.query_rule_obj.title}, timepoint={self.timepoint})"
        )

    def __str__(self):
        return (
            f"model={self.query_rule_obj.model_cls._meta.label_lower}, "
            f"query_rule={self.query_rule_obj.title}, timepoint={self.timepoint}"
        )

    @property
    def handler(self):
        return site_data_manager.get_rule_handler(self.query_rule_obj.rule_handler_name)

    def run_handler(self):
        """Run handler for each subject_identifier / visit_schedule / timepoint.

        Will create data queries if needed.
        """
        created = 0
        resolved = 0
        for subject_identifier in self.subject_identifiers:
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=subject_identifier
            )
            handler = self.handler(
                query_rule_obj=self.query_rule_obj,
                registered_subject=registered_subject,
                visit_schedule_obj=self.visit_schedule_obj,
                visit_code_sequence=self.visit_code_sequence,
                now=self.now,
            )
            handler.run()
            created += handler.created_counter
            resolved += handler.resolved_counter
        return created, resolved
