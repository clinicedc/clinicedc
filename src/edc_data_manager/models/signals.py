from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from edc_constants.constants import OPEN, NEW, FEEDBACK

from ..rule import RuleRunner
from .data_query import DataQuery
from .query_rule import CrfQueryRule, RequisitionQueryRule
from .query_visit_schedule import QueryVisitSchedule


@receiver(post_save, weak=False, dispatch_uid="update_query_text")
def update_query_text(sender, instance, raw, **kwargs):

    if not raw:
        if sender in [CrfQueryRule, RequisitionQueryRule] and not instance.query_text:
            instance.query_text = instance.rendered_query_text or "query not described"
            instance.save(update_fields=["query_text"])


@receiver(post_save, weak=False, dispatch_uid="update_query_on_crf")
def update_query_on_crf(sender, instance, raw, **kwargs):

    if not raw:
        try:
            instance.visit_model_attr  # is a CRF/Requisition
        except AttributeError:
            pass
        else:
            subject_identifier = instance.visit.appointment.subject_identifier
            visit_schedule_opts = dict(
                visit_schedule_name=instance.visit.appointment.visit_schedule_name,
                schedule_name=instance.visit.appointment.schedule_name,
                visit_code=instance.visit.appointment.visit_code,
                timepoint=instance.visit.appointment.timepoint,
            )
            visit_schedule = QueryVisitSchedule.objects.get(**visit_schedule_opts)
            data_query = DataQuery.objects.filter(
                id__isnull=False,
                rule_generated=True,
                subject_identifier=subject_identifier,
                visit_schedule=visit_schedule,
                data_dictionaries__model=sender._meta.label_lower,
                site_response_status__in=[NEW, OPEN, FEEDBACK],
            ).first()
            if data_query:
                query_rule = CrfQueryRule.objects.get(
                    reference=data_query.rule_reference
                )
                runner = RuleRunner(query_rule)
                runner.run_one(
                    subject_identifier=subject_identifier, **visit_schedule_opts
                )
