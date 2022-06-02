from edc_registration.models import RegisteredSubject
from tqdm import tqdm

from ..site_data_manager import site_data_manager


class QueryRuleWrapper:
    def __init__(
        self,
        query_rule_obj=None,
        subject_identifiers=None,
        visit_schedule_obj=None,
        timepoint=None,
        entry_status=None,
        now=None,
        verbose=None,
    ):
        self.now = now
        self.query_rule_obj = query_rule_obj
        self.subject_identifiers = subject_identifiers
        self.visit_schedule_obj = visit_schedule_obj
        self.timepoint = timepoint
        self.entry_status = entry_status
        self.verbose = verbose

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"model={self.query_rule_obj.model_cls._meta.label_lower}, "
            f"query_rule={self.query_rule_obj.title}, timepoint={self.timepoint}, "
            f"{self.entry_status}, "
            f"subject_identifiers={self.count(self.subject_identifiers)})"
        )

    def __str__(self):
        return (
            f"model={self.query_rule_obj.model_cls._meta.label_lower}, "
            f"query_rule={self.query_rule_obj.title}, timepoint={self.timepoint}, "
            f"{self.entry_status}, "
            f"subject_identifiers={self.count(self.subject_identifiers)})"
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
        total = self.count(self.subject_identifiers)
        for value in tqdm(
            self.get_subject_identifiers(), total=total, disable=not self.verbose
        ):
            registered_subject = RegisteredSubject.objects.get(
                subject_identifier=value["subject_identifier"]
            )
            handler = self.handler(
                query_rule_obj=self.query_rule_obj,
                registered_subject=registered_subject,
                visit_schedule_obj=self.visit_schedule_obj,
                now=self.now,
            )
            handler.run()
            created += handler.created_counter
            resolved += handler.resolved_counter
        return created, resolved

    @property
    def get_subject_identifiers(self):
        """Returns an iterable of dictionaries of
        {subject_identifier: value, ...}.
        """
        return getattr(
            self.subject_identifiers,
            "all",
            lambda: [{"subject_identifier": s for s in self.subject_identifiers}],
        )

    @staticmethod
    def count(qs_or_list):
        try:
            cnt = qs_or_list.count()
        except (TypeError, AttributeError):
            cnt = len(qs_or_list)
        return cnt
