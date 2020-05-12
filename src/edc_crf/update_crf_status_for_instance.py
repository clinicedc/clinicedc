from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import COMPLETE, INCOMPLETE

from .models import CrfStatus


def update_crf_status_for_instance(instance):
    opts = dict(
        subject_identifier=instance.subject_visit.subject_identifier,
        visit_schedule_name=instance.subject_visit.visit_schedule_name,
        schedule_name=instance.subject_visit.schedule_name,
        visit_code=instance.subject_visit.visit_code,
        visit_code_sequence=instance.subject_visit.visit_code_sequence,
        label_lower=instance._meta.label_lower,
        user_created=instance.user_created,
        user_modified=instance.user_modified,
    )

    if instance.crf_status == COMPLETE:
        CrfStatus.objects.filter(**opts).delete()
    elif instance.crf_status == INCOMPLETE:
        try:
            CrfStatus.objects.get(**opts)
        except ObjectDoesNotExist:
            CrfStatus.objects.create(**opts)
