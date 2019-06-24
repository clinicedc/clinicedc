from django.conf import settings
from django.contrib.sites.models import Site
from edc_metadata.constants import REQUIRED, KEYED
from edc_metadata.models import CrfMetadata
from edc_registration.models import RegisteredSubject

from .rule_result import RuleResult
from .single_rule_handler import SingleRuleHandler
from edc_data_manager.models.query_visit_schedule import QueryVisitSchedule


class RuleRunner:
    def __init__(self, rule_object):
        self.rule_object = rule_object

    @property
    def reference(self):
        return self.rule_object.title

    def run_one(
        self,
        subject_identifier=None,
        model_cls=None,
        visit_schedule_name=None,
        schedule_name=None,
        visit_code=None,
    ):
        visit_schedule = QueryVisitSchedule.objects.get(
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
        )
        return self.update_queries(
            {
                visit_schedule.visit_code: [
                    RuleResult(
                        model_cls=model_cls,
                        rule_object=self.rule_object,
                        rule_title=self.rule_object.title,
                        subject_identifiers=[subject_identifier],
                        visit_schedule=visit_schedule,
                    )
                ]
            }
        )

    def run(self):
        rule_results = {}
        for visit_schedule in self.rule_object.visit_schedule.all():
            results = []
            for crf_model_cls in self.rule_object.model_classes:
                missing_crfs = self.missing_crfs_by_subject_identifiers(
                    visit_schedule=visit_schedule, model_cls=crf_model_cls
                )
                keyed_by_subject_identifier = self.keyed_by_subject_identifier(
                    visit_schedule=visit_schedule, model_cls=crf_model_cls
                )
                if missing_crfs:
                    results.append(
                        RuleResult(
                            model_cls=crf_model_cls,
                            rule_object=self.rule_object,
                            rule_title=self.rule_object.title,
                            subject_identifiers=missing_crfs,
                            visit_schedule=visit_schedule,
                        )
                    )
                if keyed_by_subject_identifier:
                    results.append(
                        RuleResult(
                            model_cls=crf_model_cls,
                            rule_object=self.rule_object,
                            rule_title=self.rule_object.title,
                            subject_identifiers=keyed_by_subject_identifier,
                            visit_schedule=visit_schedule,
                        )
                    )
            if results:
                rule_results.update({visit_schedule.visit_code: results})
        return rule_results

    def update_queries(self, rule_results=None):
        """Create a DataQuery for each subject_identifier / visit_schedule.
        """
        created = 0
        resolved = 0
        rule_results = rule_results or self.run()
        for _, rule_results in rule_results.items():
            for rule_result in rule_results:
                for subject_identifier in rule_result.subject_identifiers:
                    registered_subject = RegisteredSubject.objects.get(
                        subject_identifier=subject_identifier
                    )
                    for visit_schedule in rule_result.object.visit_schedule.all():
                        handler = SingleRuleHandler(
                            registered_subject=registered_subject,
                            visit_schedule=visit_schedule,
                            rule_result=rule_result,
                        )
                        created += handler.created
                        resolved += handler.resolved
        return created, resolved

    def missing_crfs_by_subject_identifiers(self, visit_schedule=None, model_cls=None):
        """Returns a list of subject_identifiers as the diff
        of scheduled and completed.
        """
        required = self.required_by_subject_identifier(
            visit_schedule=visit_schedule, model_cls=model_cls
        )
        keyed = self.keyed_by_subject_identifier(
            visit_schedule=visit_schedule, model_cls=model_cls
        )
        return [x for x in required if x not in keyed]

    def required_by_subject_identifier(self, **kwargs):
        """Returns a list of subject_identifiers.
        """
        value_str = "subject_identifier"
        return [x.get(value_str) for x in self.required(value_str=value_str, **kwargs)]

    def keyed_by_subject_identifier(self, **kwargs):
        """Returns a list of subject_identifiers.
        """
        value_str = "subject_identifier"
        return [x.get(value_str) for x in self.keyed(value_str=value_str, **kwargs)]

    def unfilled_fields_by_subject_identifiers(self, visit_schedule, model_cls):
        pass

    def required(self, visit_schedule=None, model_cls=None, value_str=None):
        """Returns a CrfMetadata queryset.
        """
        return CrfMetadata.objects.values(value_str).filter(
            visit_schedule_name=visit_schedule.visit_schedule_name,
            schedule_name=visit_schedule.schedule_name,
            visit_code=visit_schedule.visit_code,
            site=Site.objects.get(id=settings.SITE_ID),
            model=model_cls._meta.label_lower,
            entry_status=REQUIRED,
        )

    def keyed(self, visit_schedule=None, model_cls=None, value_str=None):
        """Returns a CrfMetadata queryset.
        """
        return CrfMetadata.objects.values(value_str).filter(
            visit_schedule_name=visit_schedule.visit_schedule_name,
            schedule_name=visit_schedule.schedule_name,
            visit_code=visit_schedule.visit_code,
            site=Site.objects.get(id=settings.SITE_ID),
            model=model_cls._meta.label_lower,
            entry_status=KEYED,
        )
