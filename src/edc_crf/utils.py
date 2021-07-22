from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import COMPLETE, INCOMPLETE

from .model_mixins import CrfStatusModelMixin


def update_crf_status_for_instance(instance, crf_status):
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
        if crf_status == COMPLETE:
            crf_status_model_cls.objects.filter(**opts).delete()
        elif crf_status == INCOMPLETE:
            try:
                crf_status_model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                crf_status_model_cls.objects.create(**opts)


def update_crf_status_command(app_label=None):
    if app_label:
        app_configs = [django_apps.get_app_config(app_label)]
    else:
        app_configs = django_apps.get_app_configs()

    print("Updating CRF Status model for instances set to crf_status=incomplete")
    for app_config in app_configs:
        print(f"  * updating {app_config.name}")
        for model in app_config.get_models():
            if issubclass(model, (CrfStatusModelMixin,)):
                print(f"    - {model._meta.label_lower}")
                for obj in model.objects.filter(crf_status=INCOMPLETE):
                    update_crf_status_for_instance(obj)
