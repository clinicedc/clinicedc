from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from edc_lab.utils import get_panel_model
from edc_model.utils import is_inline_model

from ..rule import RuleRunner
from .query_rule import QueryRule

DATA_MANAGER_ENABLED = getattr(settings, "DATA_MANAGER_ENABLED", True)


@receiver(post_save, sender=QueryRule, weak=False, dispatch_uid="update_query_text")
def update_query_text(sender, instance, raw, **kwargs):
    if not raw:
        if not instance.query_text:
            instance.query_text = instance.rendered_query_text or "query not described"
            instance.save_base(update_fields=["query_text"])


@receiver(post_save, weak=False, dispatch_uid="update_query_on_crf")
def update_query_on_crf(sender, instance, raw, **kwargs):
    if not raw:
        if DATA_MANAGER_ENABLED:
            try:
                related_visit_model_attr = instance.related_visit_model_attr()
            except AttributeError:
                pass
            else:
                related_visit = getattr(instance, related_visit_model_attr, None)
                appointment = getattr(related_visit, "appointment", None)
                if appointment and not is_inline_model(instance):
                    visit_schedule_name = appointment.visit_schedule_name
                    opts = dict(
                        visit_schedule__visit_schedule_name=visit_schedule_name,
                        visit_schedule__schedule_name=appointment.schedule_name,
                        visit_schedule__visit_code=appointment.visit_code,
                    )
                    try:
                        instance.panel
                    except AttributeError:
                        opts.update(data_dictionaries__model=sender._meta.label_lower)
                    else:
                        opts.update(
                            requisition_panel=get_panel_model().objects.get(
                                name=instance.panel.name
                            )
                        )
                    for query_rule_obj in (
                        QueryRule.objects.filter(**opts)
                        .order_by("data_dictionaries__model")
                        .distinct()
                    ):
                        runner = RuleRunner(query_rule_obj)
                        runner.run_one(
                            subject_identifier=appointment.subject_identifier,
                            visit_schedule_name=appointment.visit_schedule_name,
                            schedule_name=appointment.schedule_name,
                            visit_code=appointment.visit_code,
                            timepoint=appointment.timepoint,
                        )
