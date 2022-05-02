from typing import Any

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import COMPLETE, INCOMPLETE


def update_crf_status_for_instance(instance: Any) -> None:
    """Only works for CRFs, e.g. have subject_visit."""
    if hasattr(instance, "subject_visit"):
        crf_status_model_cls = django_apps.get_model("edc_crf.crfstatus")
        opts = dict(
            subject_identifier=instance.subject_visit.subject_identifier,
            visit_schedule_name=instance.subject_visit.visit_schedule_name,
            schedule_name=instance.subject_visit.schedule_name,
            visit_code=instance.subject_visit.visit_code,
            visit_code_sequence=instance.subject_visit.visit_code_sequence,
            label_lower=instance._meta.label_lower,
        )
        if instance.crf_status == COMPLETE:
            crf_status_model_cls.objects.filter(**opts).delete()
        elif instance.crf_status == INCOMPLETE:
            try:
                crf_status_model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                crf_status_model_cls.objects.create(**opts)
